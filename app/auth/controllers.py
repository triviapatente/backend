# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from app import app, db
from app.auth.models import *
from app.exceptions import *
from app.decorators import auth_required, needs_post_values, needs_files_values
from app.preferences.models import *
from sqlalchemy import or_
from app.utils import *

auth = Blueprint("auth", __name__, url_prefix = "/auth")
account = Blueprint("account", __name__, url_prefix = "/account")
info = Blueprint("info", __name__, url_prefix = "/info")

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
    if not user:
        #se no, login fallito!
        raise LoginFailed()
    #ottengo il keychain a partire dall'utente pescato dal db, e mi chiedo se c'è
    keychain = Keychain.query.filter(Keychain.user_id == user.id).first()
    if not keychain:
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
    if u:
        raise AlreadyRegisteredUser(u, username, email)

    #i controlli son passati, posso creare l'utente e salvarlo
    def createUser():
        db.session.autoflush = True
        user = User(username = username, email = email)
        db.session.add(user)
        db.session.flush()
        #creo le preferenze dell'utente (default) e le associo all'utente
        preferences = Preferences(user_id = user.id)
        db.session.add(preferences)
        #posso creare il portachiavi dell'utente e associarlo all'utente stesso
        keychain = Keychain(user_id = user.id, lifes = app.config["INITIAL_LIFES"])
        keychain.hash_password(password)
        db.session.add(keychain)
        return jsonify(user = user, token = keychain.auth_token)

    output = doTransaction(createUser)
    if output:
        return output
    raise TPException() # trovare exception appropriata

#api(s) per le modifiche

#api per il cambio del nome (##name)
@account.route("/name/edit", methods = ["POST"])
@auth_required
@needs_post_values("name")
def changeName():
    g.user.name = g.post.get("name")
    db.session.add(g.user)
    db.session.commit()
    return jsonify(user = g.user)

#api per il cambio del cognome (##surname)
@account.route("/surname/edit", methods = ["POST"])
@auth_required
@needs_post_values("surname")
def changeSurname():
    g.user.surname = g.post.get("surname")
    db.session.add(g.user)
    db.session.commit()
    return jsonify(user = g.user)

from werkzeug.utils import secure_filename
import os
#api per il cambio dell'immagine (##image)
@account.route("/image/edit", methods = ["POST"])
@auth_required
@needs_files_values("image")
def changeImage():
    image = g.files["image"]
    #controllo sia valido (quindi che non sia un eseguibile o un file di testo ecc)
    if allowed_file(image.filename):
        #prendo l'estensione
        filename = str(g.user.username) + "." + str(image.filename.rsplit('.')[-1])
        #cambio il filename con il nome utente per due motivi: 1- univocità, 2- sicurezza, evito che sia pericoloso
        #con secure_filename mi assicuro ulteriormente della non pericolisità del nome del file
        image.filename = secure_filename(filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        try:
            image.save(path)
            g.user.image = path
            db.session.add(g.user)
            db.session.commit()
        except:
            raise ChangeFailed()
        return jsonify(user = g.user)
    else:
        raise ChangeFailed()

#define if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.')[-1] in app.config["ALLOWED_EXTENSIONS"]

#api per la richiesta della classifica italiana (globale)
@info.route("/rank/italy", methods = ["GET"])
@auth_required
def getItalianRank():
    #richiedo le prime n posizioni
    n = app.config["RESULTS_LIMIT_RANK_ITALY"]
    rank = User.query.order_by(User.score).limit(n).all()
    if g.user not in rank:
        if length(rank) < n:
            rank.append(g.user)
        else:
            rank[n - 1] = g.user
    return jsonify(rank = rank)
