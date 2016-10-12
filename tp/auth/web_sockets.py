# -*- coding: utf-8 -*-

from tp import socketio
from flask import session, g
from flask_socketio import emit, disconnect
from models import Keychain
from tp.decorators import needs_values
from tp.ws_decorators import ws_auth_required

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
@ws_auth_required
def logout(data = None):
    # rimuovo il token se presente
    session.pop("token", None)
    emit("logout", {"success": session.get("token") == None})
    disconnect() # chiude il socket, bisogna refreshare su socketio tester 
