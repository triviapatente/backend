# -*- coding: utf-8 -*-
from flask import g, request, json
from tp import socketio, app, db
from tp.ws_decorators import ws_auth_required, check_in_room
from tp.decorators import check_game_not_ended
from tp.base.utils import roomName
from tp.game.utils import *
from tp.auth.models import User
from tp.game.models import Game, Question, Round, Category, Quiz, ProposedCategory, ProposedQuestion
from tp.decorators import needs_values, fetch_models, create_session
from flask_socketio import emit, join_room, leave_room, rooms
from flask import g
from tp.base.utils import RoomType
from tp.exceptions import NotAllowed
from sqlalchemy import func, and_, asc

import tp.cron.events as cronEvents
from tp.game.events import RecentGameEvents
import pytz

@socketio.on("init_round")
@create_session
@ws_auth_required
@needs_values("SOCKET", "game")
@fetch_models(game = Game)
@check_in_room(RoomType.game, "game")
def init_round(data):
    #parametri in input
    game = g.models["game"]
    opponent = getOpponentFrom(game.id)
    #costanti
    MAX_AGE = app.config["MATCH_MAX_AGE"]
    NUMBER_OF_QUESTIONS_PER_ROUND = app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]
    NUMBER_OF_ROUNDS = app.config["NUMBER_OF_ROUNDS"]
    #round di riferimento in base all'attività precedente dell'utente
    next_number = getNextRoundNumber(game)
    #round precedente a quello di riferimento
    prev_round = Round.query.filter(Round.number == next_number - 1).filter(Round.game_id == game.id).first()
    #controllo che la partita non sia finita
    if game.ended or gameEnded(game):
        #se è finita
        #evito di fare l'update più volte
        endedNow = not game.ended
        if endedNow:
            game.ended = True
            winner = getWinner(game)
            if winner is not None:
                game.winner_id = winner.id
            db.session.add(game)
            db.session.commit()
            print(f"Game {game.id} ended. Updating scores..")
            updatedUsers = updateScore(game)
            print("User's score updated.")
            sendStimulationOnGameEnded(game, updatedUsers, cronEvents)
        #preparo l'output
        partecipations = [p.json for p in getPartecipationFromGame(game)]
        winner = User.query.filter(User.id == game.winner_id).first()
        winner_id = None
        if winner:
            winner_id = winner.id
        if endedNow:
            users = getUsersFromGame(game)
            RecentGameEvents.change(opponent)
            events.game_ended(users, game, partecipations)
        return emit("init_round", {"success": True, "max_age": MAX_AGE, "partecipations": partecipations, "ended": True, "winner_id": winner_id})
    #controllo il caso in cui si è al round 10, con domande completate, e quindi si fa riferimento all'11, ma la partita non è finita:
    #vuol dire che gli altri utenti devono ancora giocare
    if next_number > NUMBER_OF_ROUNDS:
        return emit("init_round", {"success": True, "max_age": MAX_AGE, "waiting": "game", "waiting_for": opponent})
    #ottengo il round di riferimento
    round = Round.query.filter(Round.game_id == game.id, Round.number == next_number).first()
    #caso in cui ho completato il secondo round (di cui son sicuramente dealer), ma l'avversario è ancora fermo all'1
    if next_number > 3:
        #ottengo gli utenti del match
        users = getUsersFromGame(game, User.id)
        #controllo se ci sono risposte non date dagli utenti nel round precedente a quello in cui ho appena giocato
        answered_count = Round.query.filter(Round.number == next_number - 3).filter(Round.game_id == game.id).join(Question).count()
        if answered_count != len(users) * NUMBER_OF_QUESTIONS_PER_ROUND:
            return emit("init_round", {"success": True, "max_age": MAX_AGE, "waiting": "game", "waiting_for": opponent, "round": round.json})
    need_new_round = round is None
    #se è nullo
    if need_new_round:
        #lo creo
        round = Round(game = game, number = next_number)
        #genero il dealer
        round.dealer_id = get_dealer(game, next_number)
        #se il dealer non esiste, vuol dire che non ci sono utenti che partecipano al gioco
        if round.dealer_id is None:
            raise NotAllowed()
        #lo salvo in db
        db.session.add(round)
        db.session.commit()
    game.updatedAt = datetime.now(tz = pytz.utc)
    db.session.add(game)
    db.session.commit()
    #risposta standard
    output = {"round": round.json, "max_age": MAX_AGE, "success": True, "opponent_online": isOpponentOnline(game)}
    #ottengo il dealer per usarlo successivamente
    dealer = User.query.filter(User.id == round.dealer_id).first()
    #Il dealer del turno a cui mi riferisco deve ancora giocare il precedente turno
    if prev_round and numberOfAnswersFor(round.dealer_id, prev_round.id) < NUMBER_OF_QUESTIONS_PER_ROUND:
        #invio la risposta standard più l'info che stiamo aspettando perchè altri giocatori giocano al round precedente
        output["waiting"] = "game"
        output["waiting_for"] = dealer
    #Il dealer del turno a cui mi riferisco non ha scelto la category
    elif round.cat_id is None:
        #invio la risposta standard più l'info che stiamo aspettando per la scelta della category
        output["waiting"] = "category"
        output["waiting_for"] = dealer
    #Non ho ancora giocato tutte le partite del turno a cui mi riferisco
    elif numberOfAnswersFor(g.user.id, round.id) < NUMBER_OF_QUESTIONS_PER_ROUND:
        #invio la risposta standard più l'info che devo ancora finire il round
        output["waiting"] = "game"
        output["waiting_for"] = g.user
    print(f"User {g.user.username} in init round got output:", output)
    #TODO informazione ridondante, rimuoverla quando avremo il db lato client (in tal caso basterà l'id della categoria, che è messo nel round)
    output["category"] = Category.query.filter(Category.id == round.cat_id).first()
    emit("init_round", output)


@socketio.on("get_categories")
@create_session
@ws_auth_required
@needs_values("SOCKET", "round_id", "game")
#round id, non round number!!!
@fetch_models(round_id = Round, game = Game)
@check_game_not_ended("game")
@check_in_room(RoomType.game, "game")
def get_random_categories(data):
    #ottengo i modelli dalla richiesta
    round = g.models["round_id"]
    game = g.models["game"]
    #controllo: solo il dealer può ottenere la lista delle categorie disponibili
    if round.dealer_id != g.user.id:
        raise NotAllowed()
    #ottengo le categorie proposte precedentemente per lo stesso turno, se ci sono
    proposed = Category.query.with_entities(Category).join(ProposedCategory).filter(ProposedCategory.round_id == round.id).all()
    #se non ci sono
    if len(proposed) == 0:
        ids = Round.query.filter(Round.game_id == game.id).join(Category).with_entities(Category.id).all()
        opponent = getOpponentFrom(game.id)
        #le genero random
        proposed = Category.query.with_entities(Category, getNumberOfTotalAnswersForCategory(Category, game, opponent).label("total_answers"))
        if len(ids) != 0:
            proposed = proposed.filter(~Category.id.in_(ids))
        proposed = proposed.order_by(asc("total_answers"), func.random()).limit(app.config["NUMBER_OF_CATEGORIES_PROPOSED"]).all()

        #e le aggiungo come proposed in db
        for (candidate, totalAnswers) in proposed:
            c = ProposedCategory(round_id = round.id, category_id = candidate.id)
            db.session.add(c)
        db.session.commit()
        proposed = [cat for (cat, number) in proposed]
    #dopodichè, rispondo
    proposed = sorted([p.json for p in proposed], key = lambda cat: cat.get("id"))
    print(f"User {g.user.username} got proposed categories.", proposed)
    emit("get_categories", {"categories": proposed, "success": True})

@socketio.on("choose_category")
@create_session
@ws_auth_required
@needs_values("SOCKET", "category", "game", "round_id")
@fetch_models(game = Game, round_id = Round, category = Category)
@check_game_not_ended("game")
@check_in_room(RoomType.game, "game")
def choose_category(data):
    #ottengo i modelli
    round = g.models["round_id"]
    category = g.models["category"]
    game = g.models["game"]
    opponent = getOpponentFrom(game.id)
    opponent_id = opponent.id

    proposed = ProposedCategory.query.filter(ProposedCategory.round_id == round.id).filter(ProposedCategory.category_id == category.id).first()
    if not proposed:
        raise NotAllowed()
    #se non sono il dealer, vengo buttato fuori
    if round.dealer_id != g.user.id:
        raise NotAllowed()
    #se ho già scelto la categoria, non posso più farlo
    if round.cat_id != None:
        raise NotAllowed()
    previous_opponent_turn = isOpponentTurn(game)
    #aggiorno la categoria e salvo in db
    round.cat_id = category.id
    db.session.add(round)
    game.updatedAt = datetime.now(tz = pytz.utc)
    db.session.add(game)
    db.session.commit()
    # genero le domande random, pescando da quelle della categoria richiesta
    proposed = Quiz.query.with_entities(Quiz, getNumberOfTotalAnswersForQuiz(Quiz, game, opponent).label("total_answers")).filter(Quiz.category_id == category.id).order_by(asc("total_answers"), func.random()).limit(app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]).all()
    print(proposed)
    #e le aggiungo come questions in db
    for (candidate, totalAnswers) in proposed:
        q = ProposedQuestion(round_id = round.id, quiz_id = candidate.id)
        db.session.add(q)
    db.session.commit()

    #rispondo anche con info sulla category scelta
    print(f"User {g.user.username} has choosen category.", category)
    emit("choose_category", {"success": True, "category": category})
    opponent = User.query.get(opponent_id)
    events.category_chosen([opponent], category)

    opponent_turn = isOpponentTurn(game)
    if opponent_turn != previous_opponent_turn:
        g.user = User.query.get(g.user.id)
        opponent = User.query.get(opponent_id)
        events.your_turn(game, opponent)
        RecentGameEvents.change(opponent)

@socketio.on("get_questions")
@create_session
@ws_auth_required
@needs_values("SOCKET", "round_id", "game")
@fetch_models(round_id = Round, game = Game)
@check_game_not_ended("game")
@check_in_room(RoomType.game, "game")
def get_questions(data):
    #ottengo i modelli dalla richiesta
    round = g.models["round_id"]
    if not round.cat_id:
        raise NotAllowed()
    #ottengo le domande proposte precedentemente per lo stesso turno, se ci sono
    proposed = Quiz.query.join(ProposedQuestion).outerjoin(Question, and_(Question.quiz_id == Quiz.id, Question.user_id == g.user.id, Question.round_id == round.id)).with_entities(Quiz, Question.answer).filter(ProposedQuestion.round_id == round.id).all()
    output = []
    for item in proposed:
        quiz = item[0]
        quiz.my_answer = item[1]
        quiz.answered_correctly = (quiz.my_answer == quiz.answer)
        del quiz.answer
        output.append(quiz)

    proposed = sorted([p.json for p in output], key = lambda q: q.get("id"))
    #dopodichè, rispondo
    print(f"User {g.user.username} got questions.", proposed)
    emit("get_questions", {"questions": proposed, "success": True})

@socketio.on("answer")
@create_session
@ws_auth_required
@needs_values("SOCKET", "answer", "game", "round_id", "quiz_id")
@fetch_models(game = Game, round_id = Round, quiz_id = Quiz)
@check_game_not_ended("game")
@check_in_room(RoomType.game, "game")
def answer(data):
    #ottengo i modelli
    answer = g.params["answer"]
    round = g.models["round_id"]
    game = g.models["game"]
    quiz = g.models["quiz_id"]
    opponent = getOpponentFrom(game.id)
    question = Question.query.filter(Question.round_id == round.id, Question.user_id == g.user.id, Question.quiz_id == quiz.id).first()
    proposedQuestion = ProposedQuestion.query.filter(ProposedQuestion.round_id == round.id).filter(ProposedQuestion.quiz_id == quiz.id).first()
    if not proposedQuestion:
        raise NotAllowed()
    #se ho già risposto, non posso più farlo
    if question:
        raise NotAllowed()
    question = Question(round_id = round.id, user_id = g.user.id, quiz_id = quiz.id, answer = answer)
    db.session.add(question)
    game.updatedAt = datetime.now(tz = pytz.utc)
    db.session.add(game)

    NUMBER_OF_QUESTIONS_PER_ROUND = app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]
    number_of_answers = Question.query.filter(Question.round_id == round.id).filter(Question.user_id == g.user.id).count()

    #rispondo anche dicendo se ho dato la risposta giusta o sbagliata
    print(f"User {g.user.username} answered to proposed question.", question, answer)
    correct = (quiz.answer == question.answer)
    opponent_turn = isOpponentTurn(game)
    if number_of_answers == NUMBER_OF_QUESTIONS_PER_ROUND:
        number_of_round_answers = Question.query.filter(Question.round_id == round.id).count()
        if number_of_round_answers == NUMBER_OF_QUESTIONS_PER_ROUND * 2:
            game.started = True
            db.session.add(game)
        events.round_ended(g.roomName, round)
        if opponent_turn is not None:
            RecentGameEvents.change(opponent)
    db.session.commit()
    emit("answer", {"success": True, "correct_answer": correct})
    events.user_answered(g.roomName, question, quiz)

@socketio.on("is_user_online")
@create_session
@ws_auth_required
@needs_values("SOCKET", "game", "user")
@fetch_models(game = Game, user = User)
@check_in_room(RoomType.game, "game")
def is_user_online(data):
    user = g.models["user"]
    game = g.models["game"]
    output = isUserOnline(game.id, user.id)
    emit("is_user_online", {"answer": output})


@socketio.on("round_details")
@create_session
@ws_auth_required
@needs_values("SOCKET", "game")
@fetch_models(game = Game)
@check_in_room(RoomType.game, "game")
def round_details(data):
    game = g.models["game"]
    #ottengo i round a cui ho partecipato (quelli che ho chiuso e quelli a cui non ho ancora finito di giocare), con le relative categorie
    last_round_number = getNextRoundNumber(game)
    (rounds, categories) = getRoundInfosTill(last_round_number, game)
    #ottengo gli id dei round a cui ho giocato
    round_ids = [round.id for round in rounds]
    my_answers = getMyAnswersTill(last_round_number, game)
    quiz_ids = [answer.quiz_id for answer in my_answers]
    opponents_answers = getOpponentsAnswersAt(quiz_ids, game)
    answers = my_answers + opponents_answers
    output = {"answers": answers, "categories": categories, "game": game.json, "success": True}
    #ottengo i quiz dei round in cui ho giocato
    output["quizzes"] = getQuizzesTill(last_round_number, quiz_ids, game)
    #ottengo gli utenti del gioco
    output["users"] = getUsersFromGame(game)
    output["rounds"] = rounds;
    #se il gioco è completato
    if game.ended:
        #ottengo i risultati del gioco
        output["partecipations"] = getPartecipationFromGame(game)
    return emit("round_details", output)
