# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from app import app, db
from app.auth.models import *
from app.exceptions import *
from app.decorators import auth_required, needs_post_values
from app.preferences.models import *
from sqlalchemy import or_

auth = Blueprint("auth", __name__, url_prefix = "/auth")
settings = Blueprint("settings", __name__, url_prefix = "/settings")

@auth.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

#api che effettua il login dell'utente
@auth.route("/login", methods = ["POST"])
#utilizzando il decorator che ho creato, posso fare il controllo dell'input in una riga
@needs_post_values("user", "password")
def login():
    #ottengo i valori in input
    user_identifier = g.post.get("user")
    password = g.post.get("password")
    #ottengo l'user a partire dall'email o dall'username, e mi chiedo se c'è
    user = User.query.filter(or_(User.email == user_identifier, User.username == user_identifier)).first()
    if user is None:
        #se no, login fallito!
        raise LoginFailed()
    #ottengo il keychain a partire dall'utente pescato dal db, e mi chiedo se c'è
    keychain = Keychain.query.filter(Keychain.user_id == user.id).first()
    if keychain is None:
        #se no, login fallito! NB: questa cosa non dovrebbe mai accadere, vorrebbe dire che c'è un problema a livello di registrazione
        raise LoginFailed()

    #controllo se la password dell'utente corrisponde a quella interna
    if keychain.check_password(password):
        #se si, sei loggato! Ti torno anche un token, cosi la tua sessione inizia
        return jsonify(user = user, token = keychain.auth_token)
    else:
        #se no, login fallito
        raise LoginFailed()

#metodo fittizio per testare l'autenticazione
@auth.route("/test", methods = ["POST"])
@auth_required
def randomMethod():
    return "Doing something"


#api che effettua la registrazione dell'utente
@auth.route("/register", methods = ["POST"])
#utilizzando il decorator che ho creato, posso fare il controllo dell'input in una riga
@needs_post_values("email", "username", "password")
def register():
    #ottengo i valori in input
    username = g.post.get("username")
    email = g.post.get("email")
    password = g.post.get("password")
    #vedo se ci sono altri utenti che hanno lo stesso username o la stessa password
    u = User.query.filter((User.username == username or User.email == email)).first()
    #se si, ti mando l'errore appropriato
    if u is not None:
        raise AlreadyRegisteredUser(u, username, email)

    #i controlli son passati, posso creare l'utente e salvarlo
    user = User(username = username, email = email)
    db.session.add(user)
    #creo le preferenze dell'utente (default) e le associo all'utente
    preferences = Preferences(user_id = user.id)
    db.session.add(preferences)
    #posso creare il portachiavi dell'utente e associarlo all'utente stesso
    keychain = Keychain(user_id = user.id, lifes = app.config["INITIAL_LIFES"])
    keychain.hash_password(password)
    db.session.add(keychain)
    db.session.commit()

    #spedisco all'utente le info del suo utente, e il suo token con il quale autenticarsi
    return jsonify(user = user, token = keychain.auth_token)


#api(s) per le modifiche

@settings.route("/account", methods = ["POST"])
@auth_required
# ##name, ##surname and profile ##image of ##g.user
# if some values are null, no modification is performed
@needs_post_values("name", "surname", "image")
def changeAccountInfo():
    return "hello world"
