# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from app import app, db
from app.auth.models import *
from app.exceptions import *
auth = Blueprint("auth", __name__, url_prefix = "/auth")

@auth.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

#api che effettua il login dell'utente
@auth.route("/login", methods = ["POST"])
def login():
    #prendo i parametri di autenticazione
    email = request.form.get('email')
    password = request.form.get('password')

    #gestisco i parametri missing
    if email is None:
        raise MissingParameter(["email"])
    if password is None:
        raise MissingParameter(["password"])

    #ottengo l'user a partire dall'email, e mi chiedo se c'è
    user = User.query.filter(User.email == email).first()
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


#api che effettua la registrazione dell'utente
@auth.route("/register", methods = ["POST"])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    #gestisco i parametri missing #TODO: da fare meglio
    if username is None:
        raise MissingParameter(["username"])
    if password is None:
        raise MissingParameter(["password"])
    if email is None:
        raise MissingParameter(["email"])
    #vedo se ci sono altri utenti che hanno lo stesso username o la stessa password
    u = User.query.filter((User.username == username or User.email == email)).first()
    #se si, ti mando l'errore appropriato
    if u is not None:
        raise AlreadyRegisteredUser(u, username, email)

    #i controlli son passati, posso creare l'utente e salvarlo
    user = User(username = username, email = email)
    db.session.add(user)
    db.session.commit()
    #posso creare il portachiavi dell'utente e associarlo all'utente stesso
    keychain = Keychain(user_id = user.id)
    keychain.hash_password(password)
    db.session.add(keychain)
    db.session.commit()

    #spedisco all'utente le info del suo utente, e il suo token con il quale autenticarsi
    return jsonify(user = user, token = keychain.auth_token)
