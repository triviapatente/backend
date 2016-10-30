# -*- coding: utf-8 -*-

from flask import request, session, g
from tp.auth.models import Keychain
from tp.exceptions import Forbidden
from tp.game.utils import getInvitesCountFor
from tp.rank.queries import getUserPosition
#chiave associata al token negli header http di ogni richiesta (il valore è deciso qui)
TOKEN_KEY = 'tp-session-token'
#chiamata che a partire da una richiesta ritorna il token.
#centralizzata, cosi la si può usare dappertutto
def tokenFromRequest():
    return request.headers.get(TOKEN_KEY)

def authenticate(socket = False):
    #ottengo il token, con la chiamata trovata in app.auth.utils se non parliamo di socket, nella sessione se invece ne parliamo
    if socket:
        token = session.get("token")
    else:
        token = tokenFromRequest()
    print "Got token from request: %s." % token
    #provo a verificare il token e vedere se riesco a ottenere l'user
    user = Keychain.verify_auth_token(token)
    #se non lo ottengo vuol dire che il token non è verificato
    if user is None:
        print "No user associated with token, forbidden!"
        #lancio un errore Forbidden
        raise Forbidden()
    print "User %s associated with token." % user.username
    #in caso contrario, salvo l'utente nelle variabili della richiesta. ora le info dell'utente che la sta effettuando sono accessibili in tutto il context della richiesta corrente
    g.user = user

def get_connection_values(user):
    if not user:
        return {}
    output = {}
    output["invites"] = getInvitesCountFor(user)
    output["global_rank_position"] = getUserPosition(user)
    #TODO: add rank on friends
    return output
