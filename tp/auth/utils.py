# -*- coding: utf-8 -*-

from flask import request, session, g
from tp import db
from tp.auth.social.facebook.utils import FBManager
from tp.auth.models import *
from tp.preferences.models import *
from tp.exceptions import Forbidden
from tp.game.utils import getInvitesCountFor
from tp.rank.queries import getUserPosition
from tp.stats.queries import getCategoryPercentages
from tp.preferences.queries import getPreferencesFromUser
#chiave associata al token negli header http di ogni richiesta (il valore è deciso qui)
TOKEN_KEY = 'tp-session-token'
#chiamata che a partire da una richiesta ritorna il token.
#centralizzata, cosi la si può usare dappertutto
def tokenFromRequest():
    return request.headers.get(TOKEN_KEY)

def createUser(username, email, name = None, surname = None, birth = None, password = None, image = None):
    user = User(username = username, email = email, name = name, surname = surname, birth = birth, image = image)
    db.session.add(user)
    #creo le preferenze dell'utente (default) e le associo all'utente
    preferences = Preferences(user = user)
    db.session.add(preferences)
    #posso creare il portachiavi dell'utente e associarlo all'utente stesso
    keychain = Keychain(user = user, lifes = app.config["INITIAL_LIFES"])
    if password:
        keychain.hash_password(password)
    keychain.renew_nonce()
    db.session.add(keychain)
    return (user, keychain)
#ottengo il record che rappresenta il token facebook dell'utente, e se non lo trovo in db lo creo, con le info passate
def obtainFacebookToken(user, token, tokenInfos):
    tokenInstance = FacebookToken.query.filter(FacebookToken.user_id == user.id).first()
    if tokenInstance:
        return tokenInstance
    else: return FacebookToken.getFrom(user, token, tokenInfos)

#routine che crea un utente assieme al suo record facebookToken
def createFBUser(username, email, name, surname, birth, token, tokenInfos):
    image = FBManager.profileImage(tokenInfos)
    (user, keychain) = createUser(username = username, email = email, name = name, surname = surname, birth = birth, image = image)
    tokenInstance = obtainFacebookToken(user, token, tokenInfos)
    db.session.add(tokenInstance)
    return (user, keychain)

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
    output["stats"] = getCategoryPercentages(user)
    output["preferences"] = getPreferencesFromUser(user)
    #TODO: add rank on friends
    return output
