# -*- coding: utf-8 -*-

from app import app, db
from app.game.models import Game, Round
from app.auth.models import User

# utils per il calcolo del punteggio

# enumeration of possible results for match
from enum import Enum
class Score(Enum):
    win = 1
    draw = 0.5
    loss = 0

# dato il risultato effettivo (##effective), quello previsto (##expected) e il vecchio punteggio (##score)
# ritorna il punteggio effettivo
def new_score(effective, expected, score, k):
    return rating + k * (effective - expected)

# calcola il fattore moltiplicativo per quella data partita, in funzione del numero di partite (##n_games) disputate tra i due giocatori
def k_factor(n_games, friendly_game):
    min_k = app.config["MIN_MULTIPLIER_FACTOR"]
    max_k = app.config["MAX_MULTIPLIER_FACTOR"]
    if n_games > min_k:
        n_games = max_k - min_k
    return (max_k - n_games) / (1 + friendly_game)

# funzione per calcolare la probabilità di vittoria dati:
# ##rating_A (punteggio del giocatore A), ##rating_B (punteggio del giocatore B) ed il ##range di ricerca
def expectedScore(rating_A, rating_B, range):
  expected_A = 1 / ( 1 + 10**((rating_b - rating_a) / range))
  expected_B = 1 / ( 1 + 10**((rating_a - rating_b) / range))
  return expected_A, expected_B


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
