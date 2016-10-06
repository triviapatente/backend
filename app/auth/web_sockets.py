# -*- coding: utf-8 -*-

from app import socketio
from flask import session, g
from flask_socketio import emit
from models import Keychain
from app.decorators import needs_values

@socketio.on("auth")
@needs_values("SOCKET", "token")
def authenticate(data):
    token = g.params["token"]
    user = Keychain.verify_auth_token(token)
    if user:
        #assegno il token alla sessione
        session["token"] = token
        print "User %s just connected to socketio server." % user.username
    emit("auth", {"success": user != None})

@socketio.on("logout")
def logout(data = None):
    # rimuovo il token se presente
    session.pop("token", None)
    emit("disconnect", {"success": session.get("token") == None})
