# -*- coding: utf-8 -*-

from flask import request, g
from functools import wraps
from tp import db
from flask_socketio import rooms
from tp.game.models import Partecipation
from tp.events.models import RoomParticipation
from tp.exceptions import ChangeFailed, NotAllowed
from tp.auth.utils import authenticate
from tp.base.utils import roomName, getUsersFromRoom, RoomType
#per controllare che l'utente possa accedere alla room alla quale vuole accedere
def filter_input_room(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #parametri della richiesta socket
        params = request.event["args"][0]
        body = params.get("body")
        id = body.get("id")
        type = body.get("type")
        if type != "game":
            raise NotAllowed()
        elif id is None:
            return f(*args, **kwargs)
        else:
            partecipation = Partecipation.query.filter(Partecipation.user_id == g.user.id, Partecipation.game_id == id).first()
            print "game_id", id
            print "partecipation", partecipation
            #se l'id non è settato, mi viene ritornato un valore diverso da none se la room ha un nome sensato, se l'id è settato invece, mi deve ritornare un array con length > 0
            if partecipation is not None:
                g.roomName = roomName(id, "game")
                return f(*args, **kwargs)
            else:
                raise NotAllowed()
    return decorated_function

#funzione che controlla che l'utente sia nella room giusta per effettuare la richiesta
def check_in_room(type, key):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            id = g.params[key]
            room = roomName(id, type)
            if type != RoomType.game:
                raise NotAllowed()
            partecipation = RoomParticipation.query.filter(RoomParticipation.socket_id == request.sid, RoomParticipation.game_id == id).first()
            if not partecipation:
                raise NotAllowed()
            g.roomName = room
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def ws_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authenticate(socket = True)
        #f è la rappresentazione della funzione a cui hai messo sopra @auth_required. ora che hai finito tutto, può essere eseguita
        return f(*args, **kwargs)
    return decorated_function
