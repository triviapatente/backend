# -*- coding: utf-8 -*-

from app import socketio
from flask import session
from flask_socketio import emit
from models import Keychain

@socketio.on("auth")
#TODO: add decorator that checks for parameters
def authenticate(data):
    token = data["token"]
    user = Keychain.verify_auth_token(token)
    if user:
        #assegno il token alla sessione
        session["token"] = token
        print "User %s just connected to socketio server." % user.username
    emit("auth", {"success": user != None})
