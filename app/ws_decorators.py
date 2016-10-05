# -*- coding: utf-8 -*-

from flask import request, g
from functools import wraps
from app.game.models import Game
from app.auth.models import User
from app.exceptions import ChangeFailed

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
        if type == "game":
            enabled = Game.query.filter(Game.id == id, User.games.any(User.id == g.user.id)).count() > 0
        else:
            enabled = False
        if enabled:
            g.roomName = roomName(id, type)
            return f(*args, **kwargs)
        else:
            raise ChangeFailed()
    return decorated_function


def ws_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authenticate(socket = True)
        #f è la rappresentazione della funzione a cui hai messo sopra @auth_required. ora che hai finito tutto, può essere eseguita
        return f(*args, **kwargs)
    return decorated_function
