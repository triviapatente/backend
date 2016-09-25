# -*- coding: utf-8 -*-

from app import app

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
