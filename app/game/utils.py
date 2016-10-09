# -*- coding: utf-8 -*-

from app import app, db
from app.game.models import Game, Round
from app.auth.models import User
from sqlalchemy import or_, and_
from random import randint
from app.utils import doTransaction

# utils per il calcolo del punteggio

# enumeration of possible results for match
from enum import Enum
class Score(Enum):
    win = 1
    draw = 0.5
    loss = 0

# dato il risultato effettivo (##effective), quello previsto (##expected) e il vecchio punteggio (##score)
# ritorna il punteggio effettivo
def new_score(effective, expected, k, score):
    return score + k * (effective - expected)

# calcola il fattore moltiplicativo per quella data partita, in funzione del numero di partite (##n_games) disputate tra i due giocatori
def k_factor(n_games, friendly_game):
    min_k = app.config["MIN_MULTIPLIER_FACTOR"]
    max_k = app.config["MAX_MULTIPLIER_FACTOR"]
    if n_games > min_k:
        n_games = max_k - min_k
    return (max_k - n_games) / (1 + friendly_game)

# funzione per calcolare la probabilità di vittoria di A dati:
# ##score_A (punteggio del giocatore A), ##score_B (punteggio del giocatore B) ed il ##scoreRange di ricerca
def expectedScore(score_A, score_B, scoreRange):
    expected = 1 / ( 1 + 10**((score_B - score_A) / scoreRange))
    return expected

#metodo che genera il dealer del round (colui che può scegliere la categoria)
##game_id: id del gioco di appartenenza, ##number: numero del round
def get_dealer(game, number):
    #se il numero del round è <= 1 (primo round, di solito ha 1 come numero), allora è il creator a essere dealer
    if number <= 1:
        return game.creator_id
    else: #altrimenti
        #ottengo gli utenti che partecipano al gioco
        users = User.query.with_entities(User.username, User.id).join((Game, User.games)).filter(Game.id == game.id).order_by(User.username).all()
        #li conto
        n_users = len(users)
        #se sono 0 (impossibile ma è gestito), il dealer è nullo
        if n_users == 0:
            return None
        #ottengo il round precedente a quello richiesto
        previous_round = Round.query.with_entities(Round.dealer_id).filter(Round.number == number - 1).filter(Round.game_id == game.id).one()
        #ottengo la posizione del precedente dealer nell'array ordinato degli utenti
        previous_dealer_position = [k for (k, v) in enumerate(users) if v.id == round.dealer_id][0]
        #ritorno l'utente immediatamente successivo
        return users[(previous_dealer_position + 1) % n_users]

# funzione che cerca un accoppiamento all'interno del ##range per l'utente ##userA
# ##prevRange serve a evitare di considerare i range già considerati
def searchInRange(prevRange, scoreRange, userA):
    # ottengo gli utenti compresi nel range ([userA.score-range;userA.score-prevRange] U [userA.score+prevRange;userA.score+range])
    users = User.query.filter(or_(and_(User.score < (userA.score + scoreRange), User.score > (userA.score + prevRange)), and_(User.score > userA.score - scoreRange, User.score < userA.score - prevRange)))
    allUsersInRange = users.all()
    candidates = allUsersInRange
    # vedo se ci sono users nel range
    if allUsersInRange:
        # ci sono, favorisco i giocatori con un numero di partite superiore alla media
        # calcolo il numero di partite per giocatore e la somma totale
        scoreSum = 0
        users_games = {}
        for user in allUsersInRange:
            nGames = getNumberOfActiveGames(user)
            users_games[user] = nGames
            scoreSum = scoreSum + nGames
        # calcolo la media
        scoreAverage = scoreSum / len(allUsersInRange)
        # trovo gli utenti sopra la media
        userOverAverage = []
        for user in allUsersInRange:
            if users_games[user] > scoreAverage:
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

# funzione che ritorna il numero di partite attive di un giocatore (##user)
def getNumberOfActiveGames(user):
    # prendo le partite dell'utente
    games = Game.query.filter(Game.users.any(User.id == user.id))
    # le filtro per quelle attive (non hanno un winner)
    activeGames = games.filter(Game.ended == False)
    # ritorno il numero delle partite
    return activeGames.count()

# funzione che ritorna il numero di partite tra due giocatori (##user_A, ##user_B)
def getNumberOfGames(user_A, user_B):
    # prendo le partite dell'utente e le conto
    return Game.query.filter(Game.users.any(User.id == user_A.id)).filter(Game.users.any(User.id == user_B.id)).count()

# funzione che aggiorna il punteggio di una partita (##game) trovata con un abbinamento in ##scoreRange
def updateScore(game, scoreRange):
    # prendo gli utenti di una partita
    users = getUsersFromGame(game)
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
        for user in params["users"]:
            # assegno ad ogni utente il suo nuovo punteggio
            user.score = new_score(params["updateParams"][user]["effectiveResult"], params["updateParams"][user]["expectedScore"], params["updateParams"][user]["k_factor"], user.score)
            db.session.add(user)
        return users
    return doTransaction(newScores, **{"users": users, "updateParams": updateParams})

# funzione che ritorna gli utenti di una partita (##game)
def getUsersFromGame(game):
    # return User.query.with_entities(User).join(Game).filter(Game.id == game.id).all()
    return User.query.filter(User.games.any(id = game.id)).all()

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
