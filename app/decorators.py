# -*- coding: utf-8 -*-

from flask import g, request
from functools import wraps

from app.auth.utils import tokenFromRequest as getToken
from app.auth.models import Keychain
from app.exceptions import MissingParameter, Forbidden
#decorator che serve per markare una api call in modo che avvenga un controllo sul token mandato dall'utente prima della sua esecuzione.
#per metterlo in funzione basterà anteporre @auth_required alla stessa
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #ottengo il token, con la chiamata trovata in app.auth.utils
        token = getToken()
        #provo a verificare il token e vedere se riesco a ottenere l'user
        user = Keychain.verify_auth_token(token)
        #se non lo ottengo vuol dire che il token non è verificato
        if user is None:
            #lancio un errore Forbidden
            raise Forbidden()
        #in caso contrario, salvo l'utente nelle variabili della richiesta. ora le info dell'utente che la sta effettuando sono accessibili in tutto il context della richiesta corrente
        g.user = user
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
