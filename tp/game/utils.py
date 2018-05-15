# -*- coding: utf-8 -*-

from tp import app, db, socketio
from tp.game.models import Game, Round, Partecipation, LastTrainingAnswer, TrainingAnswer, Question, Quiz, Category, ProposedQuestion, Training
from tp.auth.models import User
from sqlalchemy import or_, and_, func, select
from sqlalchemy.orm import aliased
from sqlalchemy.sql import column
from sqlalchemy.sql.expression import label, exists, case
from sqlalchemy import func, desc, asc
from random import randint
from flask import g
from tp.utils import doTransaction
from tp.exceptions import NotAllowed
from distutils.util import strtobool
from tp.events.models import Socket, RoomParticipation
from tp.rank.queries import getRank, getLastGameResultJoin
from tp import TPJSONEncoder
from flask.json import jsonify
from datetime import datetime, timedelta
#metodo transazionale per la creazione di una partita
def createGame(opponents):
    new_game = Game(creator = g.user)
    #spedisco tutti gli inviti
    for opponent in opponents:
        #TODO: gestire la logica per mandare le notifiche push a chi di dovere
        p = Partecipation(user = opponent)
        new_game.users.append(p)
    p = Partecipation(user = g.user)
    new_game.users.append(p)
    db.session.add(new_game)
    round = Round(game = new_game, number = 1)
    #genero il dealer
    round.dealer_id = g.user.id
    #lo salvo in db
    db.session.add(round)
    return new_game

def getPendingGamesQuery(userA, userB, count = False):
    query = Game.query
    if count:
        query = query.with_entities(func.count(Game.id))
    return query.filter(Game.ended == False, Game.started == False).join(Partecipation, Partecipation.game_id == Game.id).filter(or_(and_(Game.creator_id == userA.id, Partecipation.user_id == userB.id), and_(Game.creator_id == userB.id, Partecipation.user_id == userA.id)))

def createTraining(answers):
    new_training = Training(user = g.user)
    for (quiz, item) in answers.items():
        answer = item.get("answer")
        index = item.get("index")
        if not isinstance(answer, bool):
            answer = None
        q = TrainingAnswer(quiz_id = long(quiz), answer = answer, order_index = index)
        new_training.answers.append(q)
        lastQ = LastTrainingAnswer.query.filter(LastTrainingAnswer.quiz_id == quiz, LastTrainingAnswer.user_id == g.user.id).first()
        if not lastQ:
            lastQ = LastTrainingAnswer(user = g.user, quiz_id = quiz)
        lastQ.answer = answer
        db.session.add(lastQ)
    db.session.add(new_training)
    return new_training

def sanitizeSuggestedUsers(users):
    output = []
    for (user, last_game_winner) in users:
        if last_game_winner is not None:
            user.last_game_won = (last_game_winner == g.user.id)
        output.append(user)
    return output

def getQuestionsOfTraining(id):
    questions = Quiz.query.with_entities(Quiz, Category.hint, TrainingAnswer.answer.label("my_answer"), TrainingAnswer.order_index.label("order_index")).join(Category).join(TrainingAnswer).filter(TrainingAnswer.training_id == id).order_by(asc("order_index")).all()
    output = []
    for (question, catHint, my_answer, order_index) in questions:
        question.my_answer = my_answer
        question.category_hint = catHint
        question.order_index = order_index
        output.append(question)
    return output
def getErrorsForTraining(t):
    return db.session.query(func.count(Quiz.id)).outerjoin(TrainingAnswer, and_(or_(TrainingAnswer.answer != Quiz.answer, TrainingAnswer.answer == None), TrainingAnswer.quiz_id == Quiz.id)).filter(TrainingAnswer.training_id == t.id)
def getTrainings():
    #SELECT training.*,
    #        (SELECT count(traininganswer.*)
    #         FROM traininganswer
    #         RIGHT JOIN quiz
    #            ON traininganswer.quiz_id = quiz.id
    #            AND traininganswer.answer != quiz.answer
    #         WHERE traininganswer.training_id = training.id) AS errors
    #FROM training
    #WHERE training.user_id = 2;
    errorQuery = getErrorsForTraining(Training).label("numberOfErrors")
    trainings = Training.query.with_entities(Training, errorQuery).filter(Training.user_id == g.user.id).all()
    output = []
    for (training, errors) in trainings:
        training.numberOfErrors = errors
        output.append(training)
    return output
def getTrainingStats(trainings = None):
    if trainings is None:
        trainings = getTrainings()
    TOTAL = app.config["TRAINING_STATS_TOTAL"]
    CORRECT = app.config["TRAINING_STATS_NO_ERRORS"]
    ERRORS_12 = app.config["TRAINING_STATS_1_2_ERRORS"]
    ERRORS_34 = app.config["TRAINING_STATS_3_4_ERRORS"]
    ERRORS_MORE = app.config["TRAINING_STATS_MORE_ERRORS"]
    output = {TOTAL: len(trainings), CORRECT: 0, ERRORS_12: 0, ERRORS_34: 0, ERRORS_MORE: 0}
    for training in trainings:
        if training.numberOfErrors == 0:
            output[CORRECT] += 1
        elif training.numberOfErrors <= 2:
            output[ERRORS_12] += 1
        elif training.numberOfErrors <= 4:
            output[ERRORS_34] += 1
        elif training.numberOfErrors > 4: #just to clarify that we are not handling null values
            output[ERRORS_MORE] += 1
    return output

def generateRandomQuestionsForTraining(number):
    return Quiz.query.with_entities(Quiz, Category.hint).join(Category).order_by(func.random()).limit(number).all();
def generateUserQuestionsForTraining(number):
    #SELECT *
    #FROM quiz
    #WHERE EXISTS (SELECT 1
    #              FROM lasttraininganswer
    #               WHERE answer != quiz.answer
    #               AND user_id = 2
    #               AND quiz_id = quiz.id)
    #       OR NOT EXISTS (SELECT 1
    #                      FROM traininganswer
    #                      JOIN training ON training.id = traininganswer.training_id
    #                      WHERE traininganswer.quiz_id = quiz.id
    #                      AND training.user_id = 2
    #                       AND traininganswer.answer IS NOT NULL))
    #LIMIT 40
    firstSubQuery = LastTrainingAnswer.query.filter(LastTrainingAnswer.quiz_id == Quiz.id, LastTrainingAnswer.answer != Quiz.answer, LastTrainingAnswer.user_id == g.user.id)
    secondSubQuery = TrainingAnswer.query.join(Training).filter(TrainingAnswer.quiz_id == Quiz.id, TrainingAnswer.answer != None, Training.user_id == g.user.id)
    output = Quiz.query.with_entities(Quiz, Category.hint).join(Category).filter(or_(firstSubQuery.exists(), ~secondSubQuery.exists())).order_by(func.random()).limit(number).all()
    if len(output) < number:
        return generateRandomQuestionsForTraining(number)
    return output
def generateQuestionsForTraining(random):
    number = app.config["NUMBER_OF_QUESTIONS_FOR_TRAINING"]
    output = []
    if random is True:
        output = generateRandomQuestionsForTraining(number)
    else:
        output = generateUserQuestionsForTraining(number)
    items = []
    for (quiz, catHint) in output:
        quiz.category_hint = catHint
        items.append(quiz)
    return items

def getMostPlayedUser(except_user):
    a = aliased(Partecipation, name = "a")
    b = aliased(Partecipation, name = "b")
    query = User.query.with_entities(User.id, func.count(a.createdAt).label("count")).join(a, a.user_id == User.id).join(b, b.game_id == a.game_id).join(Game, Game.id == b.game_id).filter(b.user_id == g.user.id)
    result = query.filter(Game.started == True, User.id != g.user.id, User.id != except_user.id).group_by(User.id).order_by(desc("count")).first();
    user_id = None
    if result is not None:
        (user_id, count) = result
    if user_id is not None:
        return User.query.get(user_id)
    return None
def getMostValuableUsersForMe():
    limit = app.config["RESULTS_LIMIT_RANK_ITALY"]
    p1 = aliased(Partecipation, name = "p1")
    p2 = aliased(Partecipation, name = "p2")
    u = aliased(User, name = "u")
    gameWithMe = db.session.query(p2).filter(p2.game_id == p1.game_id, p2.user_id == g.user.id).exists();
    last_game_date = db.session.query(p1).with_entities(func.max(p1.createdAt)).filter(p1.user_id == u.id, p1.user_id != g.user.id).filter(gameWithMe).label("last_game_date")
    output = db.session.query(u).with_entities(u, last_game_date, getLastGameResultJoin(u)).filter(last_game_date != None).order_by(desc("last_game_date")).limit(limit).all();
    items = []
    for (user, last_game_date, last_game_winner_id) in output:
        if last_game_winner_id is not None:
            user.last_game_won = (last_game_winner_id == g.user.id)
        items.append(user)
    return items

def getSuggestedUsers(user):
    output = getMostValuableUsersForMe()
    if len(output) == 0:
        return getRank(True)
    return output

# utils per il calcolo del punteggio
# enumeration of possible results for match
from enum import Enum
class Score(Enum):
    win = 1
    draw = 0.5
    loss = 0

# dato il risultato effettivo (##effective), quello previsto (##expected) e il coefficiente (##k)
# ritorna l'incremento
#def score_increment(effective, expected, k):
#    return int(k * (effective - expected) + app.config["BONUS_SCORE"])

# calcola il fattore moltiplicativo per quella data partita, in funzione del numero di partite (##n_games) disputate tra i due giocatori
# ##friendly_game definisce se la partita è un'amichevole ed influisce sul fattore moltiplicativo
#def k_factor(n_games, friendly_game):
#    min_k = app.config["MIN_MULTIPLIER_FACTOR"]
#    max_k = app.config["MAX_MULTIPLIER_FACTOR"]
#    if n_games > min_k:
#        n_games = max_k - min_k
#    return (max_k - n_games) / (1 + friendly_game)

# funzione per calcolare la probabilità di vittoria di A dati:
# ##score_A (punteggio del giocatore A), ##score_B (punteggio del giocatore B) ed il ##scoreRange di ricerca
# in caso di ##friendly_game si fa tendere l'expected score a 0.5
#def expectedScore(score_A, score_B, scoreRange, friendly_game = False):
#    return 1 / ( 1 + 10**((score_B - score_A) /(scoreRange + 10000000 * friendly_game)))

# funzione che ritorna l'utente con lo score più alto del ##game
def getFirstUser(game, *columns):
    query = User.query
    if columns:
        query = query.with_entities(*columns)
    return query.join(Partecipation).filter(Partecipation.game_id == game.id).order_by(User.score.desc()).first()

# funzione che ritorna l'utente con lo score più basso del ##game
def getLastUser(game, *columns):
    query = User.query
    if columns:
        query = query.with_entities(*columns)
    return query.join(Partecipation).filter(Partecipation.game_id == game.id).order_by(User.score).first()

# funzione che dati gli ##users ricava il range di abbinamento
#def calculateGameRange(game):
#    distance = getFirstUser(game).score - getLastUser(game).score
#    gameRange = app.config["INITIAL_RANGE"]
#    rangeInc = app.config["RANGE_INCREMENT"]
#    while gameRange < distance:
#        gameRange = gameRange + rangeInc
#    return gameRange
def get_number_of_correct_answers(user, game):
    return Question.query.join(Quiz).join(Round).filter(Round.game_id == game.id, Question.user_id == user.id, Question.answer == Quiz.answer).count()

def left_score_increment(user):
    return app.config["SCORE_ON_LEFT_GAME"]
def left_score_decrement(user):
    return -app.config["SCORE_ON_LEFT_GAME"]

def score_increment(user, userScore, opponentScore):
    if userScore >= opponentScore:
        return userScore
    else:
        return userScore - opponentScore

def get_increments(game, user, opponent, left):
    # creo un dictionary che contenga i parametri per l'update del punteggio
    # TODO v2.0: adapt for more than 2 users
    output = {}
    if left:
        output[user.id] = left_score_decrement(user)
        output[opponent.id] = left_score_increment(opponent)
        return output
    else:
        #ottengo il numero di risposte corrette nella partita per user
        userScore = get_number_of_correct_answers(user, game)
        #ottengo il numero di risposte corrette nella partita per opponent
        opponentScore = get_number_of_correct_answers(opponent, game)

        output[user.id] = score_increment(user, userScore, opponentScore)
        output[opponent.id] = score_increment(opponent, opponentScore, userScore)
        return output

def sendStimulationOnGameEnded(game, updatedUsers, events):
    opponent = getOpponentFrom(game.id)
    destination = getMostPlayedUser(except_user = opponent)
    increment = updatedUsers[g.user.id]
    limitDate = datetime.utcnow() - timedelta(days=1)
    if game.winner_id == g.user.id and destination is not None and (destination.last_game_friend_ended_game_stimulation is None or destination.last_game_friend_ended_game_stimulation <= limitDate):
        events.stimulate_on_game_end(increment, destination)
        destination.last_game_friend_ended_game_stimulation = datetime.utcnow()
        db.session.add(destination)
        db.session.commit()
# funzione che aggiorna il punteggio di una partita (##game)
def updateScore(game, left = False):
    user = g.user
    opponent = getOpponentFrom(game.id)
    increments = get_increments(game, user, opponent, left)

    # calcolo i nuovi punteggi
    def newScores(**params):
        game_id = params["game_id"]
        increments = params["increments"]
        for user_id, increment in increments.items():
            # assegno ad ogni utente il suo nuovo punteggio
            user = User.query.get(user_id)
            print "Saving user %s score increment (%d).." % (user.username, increment)
            entry = Partecipation.query.filter(Partecipation.user_id == user.id, Partecipation.game_id == game_id).first()
            user.score = max(user.score + increment, 0)
            entry.score_increment = increment
            db.session.add(entry)
            db.session.add(user)
        return increments
    return doTransaction(newScores, **{"increments": increments, "game_id": game.id})


# funzione che ritorna i record di Partecipation inerenti ad un ##game
def getPartecipationFromGame(game):
    return Partecipation.query.filter_by(game_id = game.id).all()

# funzione che ritorna gli utenti di una partita (##game)
def getUsersFromGame(game, *columns):
    game_id = game
    if isinstance(game, Game):
        game_id = game.id
    query = User.query
    if columns:
        query = query.with_entities(*columns)
    return query.join(Partecipation).filter(Partecipation.game_id == game_id).all()
#TODO: modificare, per il momento è qui per ottimizzare
def getUserCountFrom(game):
    return 2
def getMaxQuestionNumberFrom(game):
    NUMBER_OF_QUESTIONS_PER_ROUND = app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]
    return getUserCountFrom(game) * NUMBER_OF_QUESTIONS_PER_ROUND

# funzione che ritorna il risultato previsto per ##user_A dati gli ##users di una partita avvenuta in ##scoreRange
def getExpectedScoreForUser(user_A, users, scoreRange):
    # il punteggio aspettato di ogni giocatore è calcolato come la media dei punteggi aspettati di tutte le subpartite
    return sum(expectedScore(user_A.score, user_B.score, float(scoreRange)) for user_B in users if not user_B == user_A)/(len(users)-1)

# funzione che ritorna il coefficiente moltiplicativo per l'utente (##user_A) dati gli utenti (##users)
def getMultiplierFactorForUser(user_A, users):
    friendly_game = False
    # friendly_game = game.friendly_game # decommentare questa riga una volta introdotte le amichevoli
    # media dei fattori moltiplicativi di tutte le sub partite
    return sum(k_factor(getNumberOfGames(user_A, user_B), friendly_game) for user_B in users if not user_B == user_A)/(len(users)-1)

# funzione che ritorna il risultato effettivo per l'utente (##user) dato il vincitore (##winner)
def getEffectiveResult(user, winner):
    # se non esiste un vincitore
    if not winner:
        # pareggio
        return Score.draw.value
    # se l'utente è il vincitore
    elif user == winner:
        # vittoria
        return Score.win.value
    # se l'utente ha perso
    else:
        # sconfitta
        return Score.loss.value

#metodo che genera il dealer del round (colui che può scegliere la categoria)
##game_id: id del gioco di appartenenza, ##number: numero del round
def get_dealer(game, number):
    #se il numero del round è <= 1 (primo round, di solito ha 1 come numero), allora è il creator a essere dealer
    if number <= 1:
        return game.creator_id
    else: #altrimenti
        #ottengo gli utenti che partecipano al gioco
        users = User.query.join(Partecipation).filter(Partecipation.game_id == game.id).all()
        #li conto
        n_users = len(users)
        #se sono 0 (impossibile ma è gestito), il dealer è nullo
        if n_users == 0:
            return None
        #ottengo il round precedente a quello richiesto
        previous_round = Round.query.with_entities(Round.dealer_id).filter(Round.number == number - 1).filter(Round.game_id == game.id).first()
        if previous_round:
            #ottengo la posizione del precedente dealer nell'array ordinato degli utenti
            previous_dealer_position = [k for (k, v) in enumerate(users) if v.id == previous_round.dealer_id][0]
            #ritorno l'utente immediatamente successivo
            return users[(previous_dealer_position + 1) % n_users].id
        else:
            #se non c'è un previous round, non c'è dealer perchè c'è errore
            raise NotAllowed()

# funzione che cerca un accoppiamento all'interno del ##range per l'utente ##current_user
# ##prevRange serve a evitare di considerare i range già considerati
#def searchInRange(prevRange, scoreRange, current_user):
    #left_interval rappresenta a livello matematico: [current_user.score-range;current_user.score-prevRange]
#    left_interval = and_(User.score <= (current_user.score + scoreRange), User.score >= (current_user.score + prevRange))
    #right_interval rappresenta a livello matematico: [current_user.score+prevRange;current_user.score+range]
#    right_interval = and_(User.score >= current_user.score - scoreRange, User.score <= current_user.score - prevRange)
    #intervals_union rappresenta a livello matematico: ([current_user.score-range;current_user.score-prevRange] U [current_user.score+prevRange;current_user.score+range])
#    intervals_union = or_(left_interval, right_interval)
    #ottengo gli utenti nell'intervallo che non sono me
#    allUsersInRange = User.query.filter(User.id != current_user.id).filter(intervals_union).all()
#    candidates = allUsersInRange
    # vedo se ci sono users nel range
#    if allUsersInRange:
        # ci sono, favorisco i giocatori con un numero di partite superiore alla media
        # calcolo il numero di partite per giocatore
#        users_games_count = getNumberOfActiveGames(allUsersInRange)
        # calcolo la media di partite
#        gamesAverage = sum(n for n in users_games_count.values()) / len(users_games_count)
        # trovo gli utenti sopra la media
#        userOverAverage = []
#        for user in allUsersInRange:
#            if users_games_count[user.username] > gamesAverage:
#                userOverAverage.append(user)
        # se ci sono
#        if userOverAverage:
            # allora considero loro
#            candidates = userOverAverage
    # vedo se ci sono candidati (o in range o se possibile sopra la media di partite nel range)
#    if candidates:
        # se ci sono ne scelgo uno a caso
#        index = randint(0,len(candidates)-1)
#        return candidates[index]
#    else:
        # comunico che non è stato trovato un abbinamento nel range
#        return None

# funzione che ritorna il numero di partite attive dei giocatori (##users)
def getNumberOfActiveGames(users):
    # devo considerare solo i giocatori in ##users
    users_usernames = [user.username for user in users]
    # ottengo una lista di tuple (username, games_count)
    players_with_games = User.query.with_entities(User.username, func.count("user_id").label("games_count")).join(Partecipation).join(Game).filter(Partecipation.user_id == User.id and Game.ended == False and Game.started == True).group_by(User.username).all()
    # converto la lista di tuple (username, games_count) in un dictionary
    users_games_count = {}
    for (username, games_count) in players_with_games:
        users_games_count[username] = games_count
    # utenti ancora non inseriti
    userRange = [user for user in users if user.username not in users_games_count.keys()]
    # completo il dictionary con gli utenti senza partite
    for user in userRange:
        users_games_count[user.username] = 0
    return users_games_count

# funzione che ritorna il numero di partite tra due giocatori (##user_A, ##user_B)
def getNumberOfGames(user_A, user_B):
    # prendo le partite dell'utente e le conto
    return Game.query.filter(Game.users.any(User.id == user_A.id)).filter(Game.users.any(User.id == user_B.id)).count()

# funzione che definisce se una partita (##game) è finita o meno
def gameEnded(game):
    #prendo gli utenti della partita
    users = getUsersFromGame(game)
    #costanti
    numberOfRounds = app.config["NUMBER_OF_ROUNDS"]
    numberOfQuestionsPerRound = app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]
    #per ognuno di essi
    for user in users:
        #se non hanno finito l'ultimo round
        last_round_answers = Question.query.filter(Question.user_id == user.id).join(Round).filter(Round.game_id == game.id).filter(Round.number == numberOfRounds).count()
        if last_round_answers < numberOfQuestionsPerRound:
            #la partita non è finita
            return False
    #la partita è finita
    return True

# metodo che setta il winner del ##game
def getWinner(game):
    #prendo per ogni utente il numero di risposte corrette per gli utenti nella partita
    correctAnswers = getCorrectAnswers(game)
    #trovo il vincitore
    if len(correctAnswers) == 0:
        #nessuno ha risposto ad almeno una domanda correttamente --> pareggio
        return None
    if len(correctAnswers) == 1:
        #solo il primo ha risposto ad almeno una domanda correttamente --> vittoria
        return User.query.get(correctAnswers[0][0])
    (firstUserId, firstScore) = correctAnswers[0]
    (secondUserId, secondScore) = correctAnswers[1]
    if firstScore == secondScore:
        #si tratta di un pareggio
        return None
    elif firstScore > secondScore:
        return User.query.get(firstUserId)
    else:
        return User.query.get(secondUserId)

def numberOfAnswersFor(user_id, round_id):
    return Question.query.filter(Question.user_id == user_id).join(Round).filter(Round.id == round_id).count()

# metodo che calcola il numero di risposte corrette per ogni giocatore in un ##game
def getCorrectAnswers(game):
    return User.query.with_entities(User.id, func.count(Question.answer).label("number_of_correct_answer")).join(Partecipation, Partecipation.user_id == User.id).join(Question).join(Quiz, Question.quiz_id == Quiz.id).join(Round, Question.round_id == Round.id).filter(Quiz.answer == Question.answer, Round.game_id == game.id, Partecipation.game_id == game.id).group_by(User.id).all()

def getNumberOfTotalAnswersForCategory(category, game, opponent):
    ids = [g.user.id, opponent.id]
    return Question.query.with_entities(func.count(Question.quiz_id)).join(Quiz).filter(category.id == Quiz.category_id, Question.user_id.in_(ids))
def getNumberOfTotalAnswersForQuiz(quiz, game, opponent):
    ids = [g.user.id, opponent.id]
    return Question.query.with_entities(func.count(Question.quiz_id)).filter(Question.quiz_id == quiz.id, Question.user_id.in_(ids))


#obtain recent games
#TODO: add time range
def getRecentGames(user):
    #(SELECT count(question.round_id) AS count_1
    #FROM question, round AS a
    #WHERE question.round_id = a.id AND question.user_id = user.id)
    #(SELECT count(a.id) = 0 AS count_1
    #FROM round AS a, game
    #WHERE game.id = a.game_id AND a.cat_id IS NOT NULL AND (SELECT count(question.round_id) AS count_2
    #FROM question
    #WHERE question.round_id = a.id AND question.user_id = user.id) != 0)
    question_number = app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]
    overall_question_number_per_user = question_number * app.config["NUMBER_OF_ROUNDS"]
    questions = Question.query.with_entities(func.count(Question.quiz_id)).filter(Question.user_id == user.id, Question.round_id == Round.id).correlate(Round).label("questions")
    my_turn = (func.sum(case([(and_(Game.ended == False, Round.id != None, or_(Round.cat_id != None, Round.dealer_id == user.id), questions < question_number), 1)], else_ = 0)) != 0).label("my_turn")
    myAnswersCount = func.sum(case([(Question.user_id == user.id, 1)], else_ = 0)).label("myAnswersCount")
    myScore = func.sum(case([(and_(Question.user_id == user.id, Question.answer == Quiz.answer), 1)], else_ = 0)).label("myScore")
    opponentScore = func.sum(case([(and_(Question.user_id != user.id, Question.answer == Quiz.answer), 1)], else_ = 0)).label("opponentScore")
    #SELECT game.*, my_turn AS my_turn
    #FROM game JOIN partecipation ON game.id = partecipation.game_id
    #WHERE partecipation.user_id = user.id ORDER BY my_turn DESC, ended ASC, createdAt ASC LIMIT 10
    RECENT_GAMES_PER_PAGE = app.config["RECENT_GAMES_PER_PAGE"]
    active_recent_games = Game.query.join(Partecipation).outerjoin(Round).outerjoin(Question).outerjoin(Quiz).filter(Game.ended == False).filter(Partecipation.user_id == user.id).with_entities(Game, my_turn, myAnswersCount, myScore, opponentScore).group_by(Game.id).order_by(desc("my_turn"), Game.updatedAt.desc()).all()
    recent_games = []
    recent_games += active_recent_games
    if len(active_recent_games) < RECENT_GAMES_PER_PAGE:
        limit = RECENT_GAMES_PER_PAGE - len(active_recent_games)
        ended_recent_games = Game.query.join(Partecipation).outerjoin(Round).outerjoin(Question).outerjoin(Quiz).filter(Game.ended == True).filter(Partecipation.user_id == user.id).with_entities(Game, my_turn, myAnswersCount, myScore, opponentScore).group_by(Game.id).order_by(Game.updatedAt.desc()).limit(limit).all()
        recent_games += ended_recent_games
    output = []
    for game, my_turn, remaining_answers_count, my_score, opponent_score in recent_games:
        game.my_turn = my_turn != 0
        game.remaining_answers_count = overall_question_number_per_user - remaining_answers_count
        game.my_score = my_score
        game.opponent_score = opponent_score
        game.getOpponentForExport()
        output.append(game)
    return output

#ottiene il numero del round corrente se non è stato ancora completato, altrimenti il successivo
def getNextRoundNumberFor(game, user):
    NUMBER_OF_QUESTIONS_PER_ROUND = app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]
    #ottengo l'ultimo round a cui ho giocato
    prev_round = Round.query.filter(Round.game_id == game.id).join(Question).filter(Question.user_id == user.id).order_by(Round.number.desc()).first()
    if prev_round:
        number_of_answers = Question.query.filter(Question.round_id == prev_round.id).filter(Question.user_id == user.id).count()
        if number_of_answers == NUMBER_OF_QUESTIONS_PER_ROUND:
            return prev_round.number + 1
        else:
            return prev_round.number
    return 1

def getNextRoundNumber(game):
    return getNextRoundNumberFor(game, g.user)

def getOpponentFrom(game_id):
    return User.query.join(Partecipation).filter(Partecipation.game_id == game_id).filter(Partecipation.user_id != g.user.id).first()

def isOpponentTurn(game):
    opponent = getOpponentFrom(game.id)
    return isTurnOf(game, opponent)

def isTurnOf(game, user):
    number = getNextRoundNumberFor(game, user)
    NUMBER_OF_ROUNDS = app.config["NUMBER_OF_ROUNDS"]
    if number > NUMBER_OF_ROUNDS:
        return None #turno di nessuno, il game è finito
    round = Round.query.filter(Round.game_id == game.id, Round.number == number).first()
    #TODO DA VERIFICARE LA CORRETTEZZA
    if not round or round.dealer_id == user.id or round.cat_id != None:
        return True
    return False

def isOpponentOnline(game):
    opponent = getOpponentFrom(game.id)
    return isUserOnline(game.id, opponent.id)

def isUserOnline(game_id, user_id):
    participation = RoomParticipation.query.join(Socket).filter(RoomParticipation.game_id == game_id, Socket.user_id == user_id).first()
    return participation is not None

def getRoundInfosTill(round_number, game):
    output = Round.query.join(Category).with_entities(Round, Category).filter(Round.number <= round_number).filter(Round.game_id == game.id).all()
    rounds = []
    categories = []
    for (round, category) in output:
        rounds.append(round)
        categories.append(category)
    return (rounds, categories)
def numberOfAnswersForFirstRound(game, user):
    return Question.query.join(Round).filter(Round.number == 1).filter(Question.user_id == user.id).filter(Round.game_id == game.id).count()
def getMyAnswersTill(round_number, game):
    output = Question.query.join(Quiz).with_entities(Question, Quiz.answer).filter(Question.user_id == g.user.id).join(Round).filter(Round.game_id == game.id).filter(Round.number <= round_number).all()
    return [setRealAnswer(question, correct) for (question, correct) in output]

def getOpponentsAnswersAt(quiz_ids, game):
    output = Question.query.join(Quiz).with_entities(Question, Quiz.answer).filter(Question.quiz_id.in_(quiz_ids)).filter(Question.user_id != g.user.id).join(Round).filter(Round.game_id == game.id).all()
    return [setRealAnswer(question, answer) for (question, answer) in output]

def setRealAnswer(question, answer):
    question.correct = (answer == question.answer)
    return question

def manipulateQuiz(quiz, round_id, quiz_ids):
    quiz.round_id = round_id
    output = quiz.json
    if not quiz.id in quiz_ids:
        del output["answer"]
    return output

#TODO: rimuovere answer dai quiz a cui non ho ancora risposto
def getQuizzesTill(round_number, quiz_ids, game):
    quizzes = Quiz.query.join(ProposedQuestion).with_entities(Quiz, ProposedQuestion.round_id).join(Round).filter(Round.number <= round_number).filter(Round.game_id == game.id).order_by(ProposedQuestion.round_id.asc(), Quiz.id.asc()).all()
    quizzes = [manipulateQuiz(q, id, quiz_ids) for (q, id) in quizzes]
    return quizzes

def get_round_infos(round_id):
    category = Category.query.join(Round).filter(Round.id == round_id).first()
    quizzes = Quiz.query.join(Question).filter(Question.round_id == round_id).group_by(Quiz.id).all()
    return (quizzes, category)

def isRoundEnded(round):
    max_number_of_answers = getMaxQuestionNumberFrom(round.game_id)
    return Question.query.filter(Question.round_id == round.id).count() == max_number_of_answers
