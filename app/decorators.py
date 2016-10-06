# -*- coding: utf-8 -*-

from flask import g, request, session
from functools import wraps
from app import db
from app.utils import storeForMethod, outputKeyForMethod
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
#ovvero io adesso posso chiamare needs_values con un numero infinito di parametri, ed essi saranno inglobati all'interno dell'array keys
#esempio needs_values(request.form, "form", "1", "2", "3") fa in modo che keys sia uguale a ["1", "2", "3"]
#method rappresenta il tipo di richiesta: può essere GET, FILE, POST, SOCKET
def needs_values(method, *keys):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            missing = []
            #dove andare a prendere i parametri
            store = storeForMethod(method)
            #dove andare a mettere i parametri pescati
            outputKey = outputKeyForMethod(method)
            #inoltre inserisco i parametri all'interno di questo array associativo, all'interno di g, per tirarli fuori più facilmente
            output = {}
            for key in keys:
                #lo store è un array? controllo se il valore è presente (è il caso di request.files)
                missing_on_array = isinstance(store, list) and key not in store
                #lo store è una map? controllo se è presente (è il caso di request.form)
                missing_on_dict = isinstance(store, dict) and store.get(key) == None
                if missing_on_dict or missing_on_array:
                    missing.append(key)
                else:
                    output[key] = store[key]
            #necessario perchè g non supporta cose del tipo g[a]
            setattr(g, outputKey, output)
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
