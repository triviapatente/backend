# -*- coding: utf-8 -*-

from flask import request, g
from functools import wraps
from tp import db
from flask_socketio import rooms
from tp.game.models import Partecipation
from tp.exceptions import ChangeFailed, NotAllowed
from tp.auth.utils import authenticate
from tp.base.utils import roomName, getUsersFromRoom
#per controllare che l'utente possa accedere alla room alla quale vuole accedere
def filter_input_room(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #parametri della richiesta socket
        params = request.event["args"][0]
        body = params.get("body")
        id = body.get("id")
        type = body.get("type")
        output = getUsersFromRoom(type, id, True)
        #se l'id non è settato, mi viene ritornato un valore diverso da none se la room ha un nome sensato, se l'id è settato invece, mi deve ritornare un array con length > 0
        if (id is None and output is not None) or output:
            g.roomName = roomName(id, type)
            return f(*args, **kwargs)
        else:
            raise NotAllowed()
    return decorated_function

#funzione che controlla che l'utente sia nella room giusta per effettuare la richiesta
def check_in_room(type, key):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            room = roomName(g.params[key], type)
            if room not in rooms():
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
