# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g, send_file, render_template
from flask_mail import Message
from tp import app, db, limiter, mail
from tp.auth.queries import *
from tp.auth.models import *
from sqlalchemy import or_
from tp.exceptions import *
from tp.decorators import auth_required, needs_values, trim_values, webpage, create_session
from tp.preferences.models import *
from tp.utils import *
from tp.auth.utils import createUser, createFBUser, obtainFacebookToken, linkUserToFB
from tp.auth.social.facebook.utils import FBManager, getFBTokenInfosFromUser
import os

auth = Blueprint("auth", __name__, url_prefix = "/auth")
fb = Blueprint("fb", __name__, url_prefix = "/fb")
account = Blueprint("account", __name__, url_prefix = "/account")
info = Blueprint("info", __name__, url_prefix = "/info")

@create_session
#api che effettua il login dell'utente
@auth.route("/login", methods = ["POST"])
#utilizzando il decorator che ho creato, posso fare il controllo dell'input in una riga
@needs_values("POST", "user", "password")
def login():
    #ottengo i valori in input
    password = g.post.get("password")
    #ottengo l'user a partire dall'email o dall'username, e mi chiedo se c'è
    user = getUserFromIdentifier(g.post.get("user").strip())
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
        print("User: ", user)
        return jsonify(user = user, token = keychain.auth_token)
    else:
        #se no, login fallito
        raise LoginFailed()

@create_session
#api che effettua la registrazione dell'utente
@auth.route("/register", methods = ["POST"])
#utilizzando il decorator che ho creato, posso fare il controllo dell'input in una riga
@needs_values("POST", "email", "username", "password")
def register():
    #ottengo i valori in input
    username = g.post.get("username").strip()
    email = g.post.get("email").strip()
    password = g.post.get("password")
    #vedo se ci sono altri utenti che hanno lo stesso username o la stessa email
    u = getUserFromUsernameOrEmail(username, email)
    #se si, ti mando l'errore appropriato
    if u:
        raise AlreadyRegisteredUser(u, username, email)
    #i controlli son passati, posso creare l'utente e salvarlo
    output = doTransaction(createUser, username = username, email = email, password = password)
    user, keychain = output
    print(f"User {user.username} has registered.", user)
    return jsonify(user = user, token = keychain.auth_token)

@create_session
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
            print(f"User {user.username} has registered.", user)
            return jsonify(user = user, token = keychain.auth_token)
        raise TPException() #TODO: trovare exception appropriata

@create_session
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
        print(f"User {g.user.username} has linked its account to Facebook")
        infos = getFBTokenInfosFromUser(g.user)
        return jsonify(infos = infos, user = g.user)
    raise TPException() #TODO: trovare exception appropriata


@create_session
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

@create_session
#richiesta da app per il forgot password. Quando chiamata, provvede a mandare la mail in cui l'utente confermerà che vuole mandare la password
@auth.route("/password/request", methods = ["POST"])
@needs_values("POST", "usernameOrEmail")
def requestNewPassword():
    value = g.post.get("usernameOrEmail").strip()
    #check if email is present in db
    user = getUserFromIdentifier(value)
    if user is not None:
        #ottengo l'email_token dell'utente
        keychain = Keychain.query.filter(Keychain.user_id == user.id).first()
        token = keychain.change_password_token
        #if so, send email to the recipient with unique token
        email = Message(
            sender = app.config["EMAIL_SENDER"],
            subject = "Richiesta cambiamento password",
            recipients = [user.email]
        )
        email.html = render_template("generated/email.html", token = token).replace("%7B%7Btoken%7D%7D", token)
        if not app.config["TESTING"]:
            mail.send(email)
        return jsonify(success = True)
    else:
        raise NotFound()

@create_session
#@auth.route("/password/", methods = ["GET"])
#def passwordPage():
#    return render_template("forgot_password/email.html")
#richiesta che viene chiamata quando l'utente preme il bottone 'Cambia password' nella mail. Provvede a mostrare la pagina per cambiare password
@auth.route("/password/change_from_email", methods = ["GET"])
@webpage("forgot_password/change.html", passwordMinChars = app.config["PASSWORD_MIN_CHARS"])
@needs_values("GET", "token")
def forgotPasswordWebPage():
    token = g.query.get("token")
    #decript token and retrieve user_id
    g.user = Keychain.verify_auth_token(token, nonce_key = "change_password_nonce")
    if g.user is None:
        raise Forbidden()
    #present web page
    return {"token": token, "user": g.user}

@create_session
#richiesta che viene chiamata quando l'utente cambia effettivamente la password da web. Cambia la password e mostra l'esito
@auth.route("/password/change_from_email", methods = ["POST"])
@webpage("forgot_password/change.html", passwordMinChars = app.config["PASSWORD_MIN_CHARS"])
@needs_values("POST", "token", "password")
def forgotPasswordWebPageResult():
    password = g.post.get("password")
    token = g.post.get("token")
    #decript token and retrieve user_id
    g.user = Keychain.verify_auth_token(token, nonce_key = "change_password_nonce")
    success = g.user is not None
    if success:
        #change password of user_id to 'password'
        keychain = Keychain.query.filter(Keychain.user_id == g.user.id).first()
        keychain.hash_password(password)
        keychain.renew_change_password_nonce()
        db.session.add(keychain)
        db.session.commit()
    else:
        raise NotAllowed()
    #return page with confirmation
    return {"success": success, "user": g.user}


#api(s) per le modifiche
@create_session
#api per il cambio del nome (##name)
@account.route("/name/edit", methods = ["POST"])
@auth_required
@trim_values("POST", False, "name")
def changeName():
    name = g.post.get("name")
    if name is not None and len(name) == 0:
        name = None;
    g.user.name = name
    db.session.add(g.user)
    db.session.commit()
    print(f"User {g.user.id} changed name to: {g.user.name}.")
    return jsonify(success = True, user = g.user)

@create_session
#api per il cambio del cognome (##surname)
@account.route("/surname/edit", methods = ["POST"])
@auth_required
@trim_values("POST", False, "surname")
def changeSurname():
    surname = g.post.get("surname")
    if surname is not None and len(surname) == 0:
        surname = None;
    g.user.surname = surname
    db.session.add(g.user)
    db.session.commit()
    print("User {g.user.id} changed surname to: {g.user.surname}")
    return jsonify(success = True, user = g.user)

@create_session
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
            print("Unable to change user image.")
            raise ChangeFailed()
        print(f"User {g.user.id} change image to: {g.user.image}.")
        return jsonify(success = True, user = g.user)
    else:
        print("User image not allowed.")
        raise FormatNotAllowed()

@create_session
@account.route("/image/<int:id>", methods = ["GET"])
@limiter.exempt
def getUserImage(id):
    user = User.query.filter(User.id == id).first()
    if not user:
        raise NotAllowed()
    elif user.image:
        return send_file("../" + user.image, add_etags=False)
    else:
        return ""

@create_session
@account.route("/user", methods = ["GET"])
@auth_required
def getCurrentUser():
    return jsonify(success = True, user = g.user)
