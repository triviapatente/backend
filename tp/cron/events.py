# -*- coding: utf-8 -*-
from tp.events.utils import EventActions
from tp.events.decorators import event
from flask import g
from tp.game.utils import getOpponentFrom
from tp.base.utils import roomName, jsonifyDates

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
