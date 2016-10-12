# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from app import app, db
from app.auth.queries import *
from app.auth.models import *
from app.exceptions import *
from app.decorators import auth_required, needs_values, needs_values
from app.preferences.models import *
from app.utils import *
import os

auth = Blueprint("auth", __name__, url_prefix = "/auth")
account = Blueprint("account", __name__, url_prefix = "/account")
info = Blueprint("info", __name__, url_prefix = "/info")

#api che effettua il login dell'utente
@auth.route("/login", methods = ["POST"])
#utilizzando il decorator che ho creato, posso fare il controllo dell'input in una riga
@needs_values("POST", "user", "password")
def login():
    #ottengo i valori in input
    password = g.post.get("password")
    #ottengo l'user a partire dall'email o dall'username, e mi chiedo se c'è
    user = getUserFromIdentifier(g.post.get("user"))
    if not user:
        #se no, login fallito!
        raise LoginFailed()
    #ottengo il keychain a partire dall'utente pescato dal db, e mi chiedo se c'è
    keychain = getKeychain(user.id)
    if not keychain:
        #se no, login fallito! NB: questa cosa non dovrebbe mai accadere, vorrebbe dire che c'è un problema a livello di registrazione
        raise LoginFailed()

    #controllo se la password dell'utente corrisponde a quella interna
    if keychain.check_password(password):
        #se si, sei loggato! Ti torno anche un token, così la tua sessione inizia
        return jsonify(user = user, token = keychain.auth_token)
    else:
        #se no, login fallito
        raise LoginFailed()

#api che effettua la registrazione dell'utente
@auth.route("/register", methods = ["POST"])
#utilizzando il decorator che ho creato, posso fare il controllo dell'input in una riga
@needs_values("POST", "email", "username", "password")
def register():
    #ottengo i valori in input
    username = g.post.get("username")
    email = g.post.get("email")
    password = g.post.get("password")
    #vedo se ci sono altri utenti che hanno lo stesso username o la stessa email
    u = getUserFromUsernameOrEmail(username, email)
    #se si, ti mando l'errore appropriato
    if u:
        raise AlreadyRegisteredUser(u, username, email)
    #i controlli son passati, posso creare l'utente e salvarlo
    def createUser():
        user = User(username = username, email = email)
        db.session.add(user)
        #creo le preferenze dell'utente (default) e le associo all'utente
        preferences = Preferences(user = user)
        db.session.add(preferences)
        #posso creare il portachiavi dell'utente e associarlo all'utente stesso
        keychain = Keychain(user = user, lifes = app.config["INITIAL_LIFES"])
        keychain.hash_password(password)
        keychain.renew_nonce()
        db.session.add(keychain)
        return (user, keychain.auth_token)

    output = doTransaction(createUser)
    if output:
        user, token = output
        return jsonify(user = user, token = token)
    raise TPException() # trovare exception appropriata

#api che effettua il logout dell'utente
@auth.route("/logout", methods = ["POST"])
@auth_required
def logout():
    keychain = getKeychain(g.user.id)
    # cambio il token
    keychain.renew_nonce()
    db.session.add(keychain)
    db.session.commit()
    return jsonify(user = g.user)

#api(s) per le modifiche

#api per il cambio del nome (##name)
@account.route("/name/edit", methods = ["POST"])
@auth_required
@needs_values("POST", "name")
def changeName():
    g.user.name = g.post.get("name")
    db.session.add(g.user)
    db.session.commit()
    return jsonify(user = g.user)

#api per il cambio del cognome (##surname)
@account.route("/surname/edit", methods = ["POST"])
@auth_required
@needs_values("POST", "surname")
def changeSurname():
    g.user.surname = g.post.get("surname")
    db.session.add(g.user)
    db.session.commit()
    return jsonify(user = g.user)

#api per il cambio dell'immagine (##image)
@account.route("/image/edit", methods = ["POST"])
@auth_required
@needs_values("FILE", "image")
def changeImage():
    image = g.files["image"]
    #prendo il nuovo filename
    filename = g.user.getFileName(image.filename)
    #controllo che il filename sia valido (se no vuol dire che aveva un'estensione non ammessa)
    if filename:
        #prendo l'estensione
        image.filename = filename
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
        raise FormatNotAllowed()

@account.route("/user", methods = ["GET"])
@auth_required
def getCurrentUser():
    return jsonify(user = g.user)

#api per la richiesta della classifica italiana (globale)
@info.route("/rank/italy", methods = ["GET"])
@auth_required
def getItalianRank():
    #chiedo la classifica (elenco utenti ordinato in base al punteggio) dei primi n utenti con le loro posizioni
    MAX = app.config["RESULTS_LIMIT_RANK_ITALY"]
    rank = getRank()
    lastScore = rank[0].score
    position = 1
    userA = None
    italianRank = []
    for userB in rank:
        if lastScore != userB.score:
            position = position + 1
            lastScore = userB.score
        # ritorno il risultato come prima, anzichè andare a ricopiare il dictionary (è immutabile) che non è neanche accettato da jsonify
        u = {}
        u["user"] = userB
        u["position"] = position
        italianRank.append(u)
        if g.user.username == userB.username:
            userA = u
    italianRank = italianRank[:MAX]
    if userA not in italianRank:
        italianRank[MAX-1] = userA
    return jsonify(rank = italianRank)
