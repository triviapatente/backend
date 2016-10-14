# -*- coding: utf-8 -*-

from flask import request, g
from functools import wraps
from tp import db
from flask_socketio import rooms
from tp.game.models import partecipation
from tp.exceptions import ChangeFailed, NotAllowed
from tp.auth.utils import authenticate
from tp.base.utils import roomName
from tp.base.utils import RoomType
#per controllare che l'utente possa accedere alla room alla quale vuole accedere
def filter_input_room(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #parametri della richiesta socket
        params = request.event["args"][0]
        id = params.get("id")
        type = params.get("type")
        enabled = True
        #unico caso al momento, ma in caso di riutilizzo del sistema room ci saranno altri casi
        if type == RoomType.game.value:
            query = db.session.query(partecipation).filter_by(user_id = g.user.id, game_id = id)
            enabled = query.count() > 0
        else:
            enabled = False
        if enabled:
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
