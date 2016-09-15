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

@auth.route("/register", methods = ["POST"])
def register():
    username = request.form.get('username', None)
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    if username is None:
        raise MissingParameter(["username"])
    if password is None:
        raise MissingParameter(["password"])
    if email is None:
        raise MissingParameter(["email"])
    u = User.query.filter((User.username == username or User.email == email)).first()
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
    print keychain.createdAt
    #spedisco all'utente le info del suo utente, e il suo token con il quale autenticarsi
    return jsonify(user = user, token = keychain.auth_token)
