# -*- coding: utf-8 -*-

from flask import g, request, session
from functools import wraps
from app import db
from app.auth.utils import authenticate
from app.auth.models import Keychain, User
from app.game.models import Game
from app.base.utils import roomName
from app.exceptions import MissingParameter, ChangeFailed
#decorator che serve per markare una api call in modo che avvenga un controllo sul token mandato dall'utente prima della sua esecuzione.
#per metterlo in funzione basterà anteporre @auth_required alla stessa
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authenticate()
        #f è la rappresentazione della funzione a cui hai messo sopra @auth_required. ora che hai finito tutto, può essere eseguita
        return f(*args, **kwargs)
    return decorated_function

#decorator che serve per controllare prima di un api call se esistono i parametri passati come argomento
#*keys è scritto cosi semplicemente perchè è il modo di python di gestire i varargs.
#ovvero io adesso posso chiamare needs_post_values con un numero infinito di parametri, ed essi saranno inglobati all'interno dell'array keys
#esempio needs_post_values("1", "2", "3") fa in modo che keys sia uguale a ["1", "2", "3"]
def needs_post_values(*keys):
    #serve una funzione intermedia perchè qui abbiamo bisogno di parametri, che vengono passati alla funzione definita nella linea sopra
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            missing = []
            #inoltre inserisco i parametri all'interno di questo array associativo, all'interno di g, per tirarli fuori più facilmente
            g.post = {}
            for key in keys:
                value = request.form.get(key)
                if value is None:
                    missing.append(key)
                else:
                    g.post[key] = value
            if missing:
                raise MissingParameter(missing)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# come quello sopra, ma per controllare la presenza di file
def needs_files_values(*keys):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            missing = []
            #inoltre inserisco i parametri all'interno di questo array associativo, all'interno di g, per tirarli fuori più facilmente
            g.files = {}
            for key in keys:
                if key not in request.files:
                    missing.append(key)
                else:
                    g.files[key] = request.files[key]
            if missing:
                raise MissingParameter(missing)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

#per controllare le coppie classi id per vedere che l'id sia valido
def fetch_models(keys):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            missing = {}
            g.models = {}
            for key, model in keys.items():
                id = request.form.get(key)
                obj = db.session.query(model).filter_by(id = id).first()
                if obj:
                    g.models[key] = obj
                else:
                    missing[key] = id
            if missing:
                raise MissingParameter(missing)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
