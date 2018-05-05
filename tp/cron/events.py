# -*- coding: utf-8 -*-
from tp.events.utils import EventActions
from tp.events.decorators import event
from flask import g
from tp.auth.models import User
from tp.game.utils import getOpponentFrom
from tp.base.utils import roomName, jsonifyDates
import random
@event("game_about_to_expire", action = EventActions.notify)
def game_about_to_expire(game, user, opponent):
    room = roomName(game.id, "game")
    g.user = user
    message = "La partita con %s scadrà fra 1 giorno! Affrettati!" % user.displayName
    push_infos = {"game": jsonifyDates(game.json), "opponent": jsonifyDates(user.json), "message": message}
    return ([opponent], None, push_infos)

@event("game_expired", action = EventActions.expired)
def game_expired(game, user, opponent):
    room = roomName(game.id, "game")
    g.user = user
    message = "La partita con %s è scaduta." % user.displayName
    push_infos = {"game": jsonifyDates(game.json), "opponent": jsonifyDates(user.json), "message": message}
    return ([opponent], None, push_infos)

stimulations = ["Hey %s, chi dorme non piglia pesci, chi non gioca a TriviaPatente non migliora!", "Ciao %s! Vuoi andare al mare in auto quest'estate? Devi allenarti e prendere la patente prima!", "Bella giornata eh %s? Oggi c'è il divieto di sosta sui libri, esercitati su TriviaPatente!", "Ciao %s! Entra su TriviaPatente per esercitarti coi tuoi amici!", "Quanto è bello giocare con gli amici e nel frattempo imparare, %s? Clicca qui e scoprilo!"]
@event("user_stimulation", action = EventActions.notify)
def stimulate_daily(user):
    message = random.choice(stimulations) % user.friendlyDisplayName
    #utente fantasma, la notifica arriva dal sistema, non un utente
    g.user = User(id = -1)
    push_infos = {"message": message}
    return ([user], None, push_infos)

@event("user_stimulation", action = EventActions.notify)
def stimulate_on_game_end(increment, destination):
    message = "Hey! Il tuo amico %s ha appena vinto una partita guadagnando %d punti! Gioca anche tu!" % (g.user.displayName, increment)
    #utente fantasma, la notifica arriva dal sistema, non un utente
    g.user = User(id = -1)
    push_infos = {"message": message}
    return ([destination], None, push_infos)
