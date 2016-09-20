# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from app import app, db
from app.auth.models import *
from app.exceptions import *
from app.decorators import auth_required, needs_post_values, needs_files_values
from app.preferences.models import *
from sqlalchemy import or_

auth = Blueprint("auth", __name__, url_prefix = "/auth")
settings = Blueprint("account", __name__, url_prefix = "/account")

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

#metodo fittizio per testare le transazioni
from app.utils import *
@auth.route("/test", methods = ["POST"])
@auth_required
@needs_post_values("name", "surname")
def randomMethod():
    def f(**dict):
        def f1(**dict):
            # user = dict["user"]
            user = g.user #per provare che non serve passare per parametri
            # session = dict["session"]
            session = db.session
            # user.name = dict["name"]
            user.name = g.post.get("name")
            session.add(user)
        def f2(**dict):
            # user = dict["user"]
            user = g.user
            # session = dict["session"]
            session = db.session
            # user.surname = dict["surname"]
            user.surname = g.post.get("surname")
            session.add(user)
        doTransaction(f1, **dict)
        doTransaction(f2, **dict)

    dict = {"name":g.post.get("name"), "surname":g.post.get("surname"), "user":g.user, "session":db.session}
    doTransaction(f, **dict)
    return jsonify(user = g.user)

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
    db.session.commit()
    #creo le preferenze dell'utente (default) e le associo all'utente
    preferences = Preferences(user_id = user.id)
    db.session.add(preferences)
    db.session.commit()
    #posso creare il portachiavi dell'utente e associarlo all'utente stesso
    keychain = Keychain(user_id = user.id, lifes = app.config["INITIAL_LIFES"])
    keychain.hash_password(password)
    db.session.add(keychain)
    db.session.commit()

    #spedisco all'utente le info del suo utente, e il suo token con il quale autenticarsi
    return jsonify(user = user, token = keychain.auth_token)


#api(s) per le modifiche

#api per il cambio del nome (##name)
@settings.route("/name/edit", methods = ["POST"])
@auth_required
@needs_post_values("name")
def changeName():
    g.user.name = g.post.get("name")
    db.session.add(g.user)
    db.session.commit()
    return jsonify(user = g.user)

#api per il cambio del cognome (##surname)
@settings.route("/surname/edit", methods = ["POST"])
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
@settings.route("/image/edit", methods = ["POST"])
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
