# -*- coding: utf-8 -*-

from app import app, db
from app.game.models import Game, Round
from app.auth.models import User
from sqlalchemy import or_, and_
from random import randint

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

# funzione che ritorna un array associativo user in ##users --> expectedScore, partita avvenuta in ##scoreRange
def getExpectedScoresForUsers(users, scoreRange):
    # calcolo i punteggi aspettati per ogni giocatore
    expectedScores = {}
    for user_A in users:
        # il punteggio aspettato di ogni giocatore è calcolato come la media dei punteggi aspettati di tutte le subpartite
        expectedScores[user_A] = sum(expectedScore(user_A.score, user_B.score, float(scoreRange)) for user_B in users if not user_B == user_A)/(len(users)-1)
    return expectedScores
