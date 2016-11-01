# -*- coding: utf-8 -*-

from tp import app, db
from tp.game.models import Game, Round, Invite, Partecipation, Question, Quiz
from tp.auth.models import User
from sqlalchemy import or_, and_, func, select
from sqlalchemy.orm import aliased
from sqlalchemy import func, desc
from random import randint
from flask import g
from tp.utils import doTransaction
from tp.exceptions import NotAllowed

#metodo transazionale per la creazione di una partita
def createGame(**params):
    new_game = Game(creator = g.user)
    opponents = params["opponents"]
    #aggiungo tutti gli avversari alla partita
    for opponent in opponents:
        partecipation = Partecipation()
        partecipation.user = opponent
        new_game.users.append(partecipation)
    #aggiungo l'utente alla partita
    partecipation = Partecipation()
    partecipation.user = g.user
    new_game.users.append(partecipation)
    db.session.add(new_game)
    #TODO: gestire la logica per mandare le notifiche push a chi di dovere
    invite = Invite(sender = g.user, receiver = opponent, game = new_game)
    db.session.add(invite)
    return new_game

# utils per il calcolo del punteggio
# enumeration of possible results for match
from enum import Enum
class Score(Enum):
    win = 1
    draw = 0.5
    loss = 0

# dato il risultato effettivo (##effective), quello previsto (##expected) e il coefficiente (##k)
# ritorna l'incremento
def score_increment(effective, expected, k):
    return k * (effective - expected) + app.config["BONUS_SCORE"]

# calcola il fattore moltiplicativo per quella data partita, in funzione del numero di partite (##n_games) disputate tra i due giocatori
# ##friendly_game definisce se la partita è un'amichevole ed influisce sul fattore moltiplicativo
def k_factor(n_games, friendly_game):
    min_k = app.config["MIN_MULTIPLIER_FACTOR"]
    max_k = app.config["MAX_MULTIPLIER_FACTOR"]
    if n_games > min_k:
        n_games = max_k - min_k
    return (max_k - n_games) / (1 + friendly_game)

# funzione per calcolare la probabilità di vittoria di A dati:
# ##score_A (punteggio del giocatore A), ##score_B (punteggio del giocatore B) ed il ##scoreRange di ricerca
# in caso di ##friendly_game si fa tendere l'expected score a 0.5
def expectedScore(score_A, score_B, scoreRange, friendly_game = False):
    return 1 / ( 1 + 10**((score_B - score_A) /(scoreRange + 10000000 * friendly_game)))

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
def calculateGameRange(game):
    distance = getFirstUser(game).score - getLastUser(game).score
    gameRange = app.config["INITIAL_RANGE"]
    rangeInc = app.config["RANGE_INCREMENT"]
    while gameRange < distance:
        gameRange = gameRange + rangeInc
    return gameRange

# funzione che aggiorna il punteggio di una partita (##game)
def updateScore(game):
    # prendo gli utenti di una partita
    users = getUsersFromGame(game)
    # calcolo lo score range
    scoreRange = calculateGameRange(game)
    # prendo il vincitore
    winner = getWinner(game)
    # creo un dictionary che contenga i parametri per l'update del punteggio
    updateParams = {}
    for user in users:
        params = {}
        params["effectiveResult"] = getEffectiveResult(user, winner)
        params["expectedScore"] = getExpectedScoreForUser(user, users, scoreRange)
        params["k_factor"] = getMultiplierFactorForUser(user, users)
        updateParams[user] = params
    # calcolo i nuovi punteggi
    # params = {"users": users, "updateParams": {"effectiveResult": effectiveResult, "expectedScore": expectedScore, "k_factor": k_factor}}
    def newScores(**params):
        users = params["users"]
        game_id = params["game_id"]
        for user in users:
            # assegno ad ogni utente il suo nuovo punteggio
            score_inc = score_increment(params["updateParams"][user]["effectiveResult"], params["updateParams"][user]["expectedScore"], params["updateParams"][user]["k_factor"])
            print "Saving user %s score increment (%d).." % (user.username, score_inc)
            entry = Partecipation.query.filter(Partecipation.user_id == user.id, Partecipation.game_id == game_id).first()
            entry.score_increment = score_inc
            db.session.add(entry)
            user.score = user.score + score_inc
            db.session.add(user)
        return users
    return doTransaction(newScores, **{"users": users, "updateParams": updateParams, "game_id": game.id})

# funzione che ritorna i record di Partecipation inerenti ad un ##game
def getPartecipationFromGame(game):
    return Partecipation.query.filter_by(game_id = game.id).all()

# funzione che ritorna gli utenti di una partita (##game)
def getUsersFromGame(game, *columns):
    query = User.query
    if columns:
        query = query.with_entities(*columns)
    return query.join(Partecipation).filter(Partecipation.game_id == game.id).all()

# funzione che ritorna l'utente vincitore di una partita (##game)
def getWinner(game):
    return User.query.filter_by(id = game.winner_id).first()

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
def searchInRange(prevRange, scoreRange, current_user):
    #left_interval rappresenta a livello matematico: [current_user.score-range;current_user.score-prevRange]
    left_interval = and_(User.score <= (current_user.score + scoreRange), User.score >= (current_user.score + prevRange))
    #right_interval rappresenta a livello matematico: [current_user.score+prevRange;current_user.score+range]
    right_interval = and_(User.score >= current_user.score - scoreRange, User.score <= current_user.score - prevRange)
    #intervals_union rappresenta a livello matematico: ([current_user.score-range;current_user.score-prevRange] U [current_user.score+prevRange;current_user.score+range])
    intervals_union = or_(left_interval, right_interval)
    #ottengo gli utenti nell'intervallo che non sono me
    allUsersInRange = User.query.filter(User.id != current_user.id).filter(intervals_union).all()
    candidates = allUsersInRange
    # vedo se ci sono users nel range
    if allUsersInRange:
        # ci sono, favorisco i giocatori con un numero di partite superiore alla media
        # calcolo il numero di partite per giocatore
        users_games_count = getNumberOfActiveGames(allUsersInRange)
        # calcolo la media di partite
        gamesAverage = sum(n for n in users_games_count.values()) / len(users_games_count)
        # trovo gli utenti sopra la media
        userOverAverage = []
        for user in allUsersInRange:
            if users_games_count[user.username] > gamesAverage:
                userOverAverage.append(user)
        # se ci sono
        if userOverAverage:
            # allora considero loro
            candidates = userOverAverage
    # vedo se ci sono candidati (o in range o se possibile sopra la media di partite nel range)
    if candidates:
        # se ci sono ne scelgo uno a caso
        index = randint(0,len(candidates)-1)
        return candidates[index]
    else:
        # comunico che non è stato trovato un abbinamento nel range
        return None

# funzione che ritorna il numero di partite attive dei giocatori (##users)
def getNumberOfActiveGames(users):
    # devo considerare solo i giocatori in ##users
    users_usernames = [user.username for user in users]
    # ottengo una lista di tuple (username, games_count)
    players_with_games = User.query.with_entities(User.username, func.count("user_id").label("games_count")).join(Partecipation).join(Game).filter(Partecipation.user_id == User.id and Game.ended == False).group_by(User.username).all()
    # converto la lista di tuple (username, games_count) in un dictionary
    users_games_count = {}
    for e in players_with_games:
        users_games_count[e.__dict__["username"]] = e.__dict__["games_count"]
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
    #per ognuno di essi
    for user in users:
        #se non hanno finito l'ultimo round
        if Question.query.filter(Question.user_id == user.id).join(Round).filter(Round.number == app.config["NUMBER_OF_ROUNDS"]).count() < app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]:
            #la partita non è finita
            return False
    #la partita è finita
    return True

# metodo che setta il winner del ##game
def setWinner(game):
    #prendo per ogni utente il numero di risposte corrette per gli utenti nella partita
    correctAnswers = getCorrectAnswers(game)
    #trovo il vincitore
    if len(correctAnswers) == 0:
        #nessuno ha risposto ad almeno una domanda correttamente --> pareggio
        return None
    if len(correctAnswers) == 1:
        #solo il primo ha risposto ad almeno una domanda correttamente --> vittoria
        return User.query.filter_by(id = correctAnswers[0][0]).first()
    if correctAnswers[0][1] == correctAnswers[1][1]:
        #si tratta di un pareggio
       return None
    else:
       return User.query.filter_by(id = correctAnswers[0][0]).first()

# metodo che calcola il numero di risposte corrette per ogni giocatore in un ##game
def getCorrectAnswers(game):
    return User.query.with_entities(User.id.label("user_id"), func.count(Question.answer).label("number_of_correct_answer")).join(Question).join(Quiz, Question.quiz_id == Quiz.id).join(Round, Question.round_id == Round.id).filter(and_(Quiz.answer == Question.answer, Round.game_id == game.id)).group_by(User.id).all()

# metodo che ritorna gli inviti per ##user
def getInvitesCountFor(user):
    return Invite.query.filter(Invite.receiver_id == user.id, Invite.accepted == None).count()
#obtain recent games
#TODO: add time range
def getRecentGames(user):
    a = aliased(Round, name = "a")
    #(SELECT count(question.round_id) AS count_1
    #FROM question, round AS a
    #WHERE question.round_id = a.id AND question.user_id = user.id)
    questions = Question.query.with_entities(func.count(Question.round_id)).filter(Question.round_id == a.id).filter(Question.user_id == user.id).as_scalar()
    #(SELECT count(a.id) = 0 AS count_1
    #FROM round AS a, game
    #WHERE game.id = a.game_id AND a.cat_id IS NOT NULL AND (SELECT count(question.round_id) AS count_2
    #FROM question
    #WHERE question.round_id = a.id AND question.user_id = user.id) != 0)
    question_number = app.config["NUMBER_OF_QUESTIONS_PER_ROUND"]
    my_turn = db.session.query(a).with_entities(func.count(a.id) != 0).filter(a.game_id == Game.id).filter(or_(Game.ended == True, and_(or_(a.cat_id != None, a.dealer_id == user.id), questions < question_number))).label("my_turn")
    #SELECT game.*, my_turn AS my_turn
    #FROM game JOIN partecipation ON game.id = partecipation.game_id
    #WHERE partecipation.user_id = user.id ORDER BY my_turn DESC, ended ASC, createdAt ASC LIMIT 10
    recent_games = db.session.query(Game).join(Partecipation).filter(Partecipation.user_id == user.id).with_entities(Game, my_turn).order_by(desc("my_turn"), Game.ended.asc(), Game.createdAt.asc()).limit(10)
    print recent_games
    output = []
    for g in recent_games:
        game = g[0]
        game.my_turn = g[1]
        game.getOpponentForExport()
        output.append(game)
    return output
