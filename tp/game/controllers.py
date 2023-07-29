# -*- coding: utf-8 -*-
from flask import jsonify, Blueprint, g, send_file
from sqlalchemy import or_, func

from tp import app, db, limiter
from tp.auth.models import User
from tp.game.models import *
from tp.utils import doTransaction
from tp.decorators import auth_required, fetch_models, needs_values, check_game_not_ended
from tp.exceptions import ChangeFailed, NotAllowed, BadParameters, AlreadyPendingGame
from tp.rank.queries import getLastGameResultJoin
from tp.game.utils import *

from tp.game.events import RecentGameEvents, tickle, new_game, game_left
from datetime import datetime, timedelta
from tp.decorators import create_session

game = Blueprint("game", __name__, url_prefix = "/game")
training = Blueprint("training", __name__, url_prefix = "/training")
quiz = Blueprint("quiz", __name__, url_prefix = "/quiz")
category = Blueprint("category", __name__, url_prefix = "/category")

@game.route("/", methods = ["GET"])
@create_session
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

@game.route("/tickle", methods = ["POST"])
@create_session
@auth_required
@needs_values("POST", "round")
@fetch_models(round = Round)
def tickleGame():
    round = g.models.get("round")
    users = getUsersFromGame(round.game_id)
    question_number = Question.query.filter(Question.round_id == round.id).count()
    game = Game.query.get(round.game_id)
    user_ids = [u.id for u in users]
    #se non appartengo al gioco
    if g.user.id not in user_ids:
        raise NotAllowed("Non appartieni al game")
    if g.user.id == round.dealer_id:
        raise NotAllowed("Questo round non è bloccabile dall'avversario, sei il dealer")
    if round.alreadyTickled:
        raise NotAllowed("C'è già stato un sollecito per questo round")
    if question_number == app.config["NUMBER_OF_QUESTIONS_PER_ROUND"] * 2:
        raise NotAllowed("Il round è completo")
    opponent = [u for u in users if u.id != g.user.id][0]
    tickle(game, opponent)
    round.alreadyTickled = True
    db.session.add(round)
    db.session.commit()
    return jsonify(success = True)

#creazione della partita
@game.route("/new", methods = ["POST"])
@create_session
@auth_required
# @needs_values("POST", "number_of_players")
@fetch_models(opponent = User)
def newGame():
    opponent = g.models["opponent"]
    pendingCount = getPendingGamesQuery(g.user, opponent).count()
    if pendingCount > 0:
        raise AlreadyPendingGame()
    game = doTransaction(createGame, **({"opponents": [opponent]}))
    if game:
        print(f"Game {game.id} created.")
        new_game(game)
        RecentGameEvents.change(opponent)
        return jsonify(success = True, game = game, user = opponent)
    else:
        raise ChangeFailed()

@game.route("/leave/decrement", methods = ["GET"])
@create_session
@auth_required
@needs_values("GET", "game_id")
@fetch_models(game_id = Game)
@check_game_not_ended("game_id")
def get_leave_score_decrement():
    game = g.models["game_id"]
    user_ids = [u.id for u in getUsersFromGame(game)]
    #se non appartengo al gioco
    if g.user.id not in user_ids:
        raise NotAllowed()
    decrement = 0
    myFirstTurnAnswers = numberOfAnswersForFirstRound(game, g.user)
    myFirstTurn = myFirstTurnAnswers < app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]
    if not myFirstTurn:
        decrement = left_score_decrement(g.user)
    return jsonify(success = True, decrement = decrement)

@game.route("/leave", methods = ["POST"])
@create_session
@auth_required
@fetch_models(game_id = Game)
@check_game_not_ended("game_id")
def leave_game():
    game = g.models["game_id"]
    users = getUsersFromGame(game)
    user_ids = [u.id for u in users]
    #se non appartengo al gioco
    if g.user.id not in user_ids:
        raise NotAllowed()
    #se ci sono più di due giocatori
    if len(users) > 2:
        #TODO: gestire la multiutenza nel gioco (versione 2.0)
        #il game non finisce, e si flagga la partecipation dell'utente, in modo che si capisce che non gioca più
        return jsonify(success = False, reason = "Version 2.0")
    #se il numero di giocatori è corretto
    elif len(users) == 2:
        opponent = [u for u in users if u.id != g.user.id][0]
        #modifico il game settandogli tra l'altro lo winner
        game.ended = True
        game.winner_id = opponent.id
        db.session.add(game)
        db.session.commit()

        myFirstTurnAnswers = numberOfAnswersForFirstRound(game, g.user)
        myFirstTurn = myFirstTurnAnswers < app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]

        if not myFirstTurn:
            #modifico i punteggi degli utenti
            updateScore(game, left = True)
        #ritorno le varie risposte
        partecipations = [p.json for p in getPartecipationFromGame(game)]
        game_left(users, game, partecipations)
        RecentGameEvents.change(opponent)
        return jsonify(success = True, ended = True, game = game, winner = opponent, partecipations = partecipations)
    #nessun avversario.. solo io nel gioco
    #NOTE: non dovrebbe succedere mai, in new_game l'opponent è obbligatorio
    return jsonify(success = False, message = "Nessun avversario in questo match!")

# ricerca aleatoria di un avversario
@game.route("/new/random", methods = ["POST"])
@create_session
@auth_required
def randomSearch():
    limitMinutes = app.config["LIMIT_MINUTES_TO_BE_CONSIDERED_ONLINE"]
    limitDate = datetime.utcnow() - timedelta(minutes=limitMinutes)
    pendingGames = getPendingGamesQuery(User, g.user, True).label("pendingGames")
    opponent = User.query.join(Socket, Socket.user_id == User.id).filter(User.id != g.user.id).filter(Socket.updatedAt >= limitDate).filter(pendingGames == 0).order_by(func.random())
    opponent = opponent.first()
    if not opponent:
        print("About to search offline opponent...")
        opponent = User.query.filter(User.id != g.user.id).filter(pendingGames == 0).order_by(func.random()).first()
    else:
        print("Online opponent found!")
    #controllo se non ho trovato nessun utente
    if opponent is None:
        print("No opponent found.")
        return jsonify(success = False)
    #eseguo la transazione con l'utente trovato
    game = doTransaction(createGame, opponents = [opponent])
    #gestisco l'output
    if game:
        print(f"Game {game.id} created.")
        new_game(game)
        RecentGameEvents.change(opponent)
        return jsonify(success = True, game = game, user = opponent)
    else:
        raise ChangeFailed()

@game.route("/recents", methods = ["GET"])
@create_session
@auth_required
def recent_games():
    #timestamp = g.query.get("timestamp")
    #if timestamp:
    #    date = datetime.fromtimestamp(float(timestamp))
    recent_games = getRecentGames(g.user)
    return jsonify(success = True, recent_games = recent_games)

@quiz.route("/image/<int:id>", methods = ["GET"])
@create_session
@limiter.exempt
def getQuizImage(id):
    image = Image.query.filter(Image.id == id).first()
    if image:
        return send_file(image.imagePath, add_etags=False)
    raise NotAllowed()

@category.route("/image/<int:id>", methods = ["GET"])
@create_session
@limiter.exempt
def getCategoryImage(id):
    category = Category.query.filter(Category.id == id).first()
    if category:
        return send_file(category.imagePath, add_etags=False)
    raise NotAllowed()

@game.route("/users/suggested", methods = ["GET"])
@create_session
@auth_required
def get_suggested_users():
    users = getSuggestedUsers(g.user)
    return jsonify(success = True, users = users)


@game.route("/users/search", methods = ["GET"])
@create_session
@needs_values("GET", "query")
@auth_required
def search_user():
    query = "%" + g.query.get("query") + "%"
    limit = app.config["RESULTS_LIMIT_RANK_ITALY"]
    criteria = or_(User.username.ilike(query), func.concat(User.name, " ", User.surname).ilike(query))
    matches = User.query.with_entities(User, getLastGameResultJoin(User)).filter(User.id != g.user.id).filter(criteria).limit(limit).all()
    output = sanitizeSuggestedUsers(matches)
    return jsonify(success = True, users = output)


@training.route("/all", methods = ["GET"])
@create_session
@auth_required
def get_trainings():
    trainings = getTrainings()
    stats = getTrainingStats(trainings)
    return jsonify(success = True, trainings = trainings, stats = stats)

@training.route("/<int:id>", methods = ["GET"])
@create_session
@auth_required
def get_training(id):
    training = Training.query.filter(Training.id == id).filter(Training.user_id == g.user.id).first()
    if training:
        questions = getQuestionsOfTraining(id)
        return jsonify(success = True, questions = questions)
    else:
        raise NotAllowed()

@training.route("/new", methods = ["GET"])
@create_session
@needs_values("GET", "random")
@auth_required
def get_training_questions():
    needsRandom = g.query.get("random")
    questions = generateQuestionsForTraining(needsRandom)
    return jsonify(success = True, questions = questions)

@training.route("/new", methods = ["POST"])
@create_session
@needs_values("JSON", "answers")
@auth_required
def answer_training():
    if g.json is None:
        raise BadParameters("Risposte mancanti")
    answers = g.json.get("answers")
    requiredNumber = app.config["NUMBER_OF_QUESTIONS_FOR_TRAINING"]
    if len(answers) != requiredNumber:
        raise BadParameters("Non ci sono 40 domande!")
    for (key, item) in answers.items():
        index = item.get("index")
        if not isinstance(key, basestring) or not isinstance(index, int):
            raise BadParameters("Input formattato male")
    quiz_ids = [long(k) for k in answers.keys()]
    quizzesCount = Quiz.query.filter(Quiz.id.in_(quiz_ids)).count()
    if quizzesCount != requiredNumber:
        raise BadParameters("Alcuni quiz non esistono in db!")
    training = doTransaction(createTraining, answers = answers)
    if training:
        training.numberOfErrors = getErrorsForTraining(training).scalar()
        return jsonify(success = True, training = training)
    else:
        raise ChangeFailed()
