# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from tp import app, db
from tp.auth.queries import *
from tp.auth.models import *
from tp.exceptions import *
from tp.decorators import auth_required, needs_values, needs_values
from tp.preferences.models import *
from tp.utils import *
from tp.auth.utils import createUser, createFBUser, obtainFacebookToken, linkUserToFB
from tp.auth.social.facebook.utils import FBManager, getFBTokenInfosFromUser
import os

auth = Blueprint("auth", __name__, url_prefix = "/auth")
fb = Blueprint("fb", __name__, url_prefix = "/fb")
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
        print "User: ", user
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
    output = doTransaction(createUser, username = username, email = email, password = password)
    if output:
        user, keychain = output
        print "User %s has registered." % user.username, user
        return jsonify(user = user, token = keychain.auth_token)
    raise TPException() # trovare exception appropriata

@fb.route("/auth", methods = ["POST"])
@needs_values("POST", "token")
def fb_auth():
    token = g.post.get("token")
    api = FBManager(token)
    profile = api.getUserInfos()
    tokenInfos = api.getTokenInfos()

    email = profile.get("email")
    first_name = profile.get("first_name")
    last_name = profile.get("last_name")
    birth = profile.get("birth_date")

    user = User.query.filter(User.email == email).first()
    if user:
        tokenInstance = obtainFacebookToken(user, token, tokenInfos)
        db.session.add(tokenInstance)
        db.session.commit()
        keychain = Keychain.query.filter(Keychain.user_id == user.id).first()
        return jsonify(user = user, token = keychain.auth_token)
    else:
        output = doTransaction(createFBUser, email = email, birth = birth, name = first_name, surname = last_name, token = token, tokenInfos = tokenInfos)
        if output:
            user, keychain = output
            print "User %s has registered." % user.username, user
            return jsonify(user = user, token = keychain.auth_token)
        raise TPException() #TODO: trovare exception appropriata

@fb.route("/link", methods = ["POST"])
@needs_values("POST", "token")
@auth_required
def link_to_fb():
    token = g.post.get("token")
    api = FBManager(token)
    profileData = api.getUserInfos()
    tokenInfos = api.getTokenInfos()
    output = doTransaction(linkUserToFB, profileData = profileData, tokenInfos = tokenInfos, token = token)
    if output:
        print "User %s has linked its account to Facebook" % g.user.username
        infos = getFBTokenInfosFromUser(g.user)
        return jsonify(infos = infos, user = g.user)
    raise TPException() #TODO: trovare exception appropriata
#api che effettua il logout dell'utente
@auth.route("/logout", methods = ["POST"])
@auth_required
def logout():
    keychain = getKeychain(g.user.id)
    # cambio il token
    keychain.renew_nonce()
    db.session.add(keychain)
    db.session.commit()
    print "%s just disconnected." % g.user.username
    return jsonify(user = g.user)

#api per il cambio della password
@auth.route("/password/edit", methods = ["POST"])
@auth_required
@needs_values("POST", "old_value", "new_value")
def changePassword():
    old_password = g.post["old_value"]
    new_password = g.post["new_value"]
    keychain = Keychain.query.filter(Keychain.user_id == g.user.id).first()
    if keychain and keychain.check_password(old_password):
        keychain.hash_password(new_password)
        keychain.renew_nonce()
        db.session.add(keychain)
        db.session.commit()
        return jsonify(token = keychain.auth_token, success = True)
    raise OldPasswordNotMatching()

#api(s) per le modifiche

#api per il cambio del nome (##name)
@account.route("/name/edit", methods = ["POST"])
@auth_required
@needs_values("POST", "name")
def changeName():
    g.user.name = g.post.get("name")
    db.session.add(g.user)
    db.session.commit()
    print "User %d change name to: %s." % (g.user.id, g.user.name)
    return jsonify(user = g.user)

#api per il cambio del cognome (##surname)
@account.route("/surname/edit", methods = ["POST"])
@auth_required
@needs_values("POST", "surname")
def changeSurname():
    g.user.surname = g.post.get("surname")
    db.session.add(g.user)
    db.session.commit()
    print "User %d change surname to: %s" % (g.user.id, g.user.surname)
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
            db.session.rollback()
            print "Unable to change user image."
            raise ChangeFailed()
        print "User %d change image to: %s." % (g.user.id, g.user.image)
        return jsonify(user = g.user)
    else:
        print "User image not allowed."
        raise FormatNotAllowed()


@account.route("/user", methods = ["GET"])
@auth_required
def getCurrentUser():
    return jsonify(user = g.user)
