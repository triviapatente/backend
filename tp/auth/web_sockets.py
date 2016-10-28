# -*- coding: utf-8 -*-

from tp import socketio
from flask import session, g, request
from flask_socketio import emit, disconnect
from models import Keychain
from tp import db
from tp.events.models import Socket
from tp.decorators import needs_values
from tp.ws_decorators import ws_auth_required
from utils import get_connection_values

@socketio.on("auth")
@needs_values("SOCKET", "token")
def authenticate(data):
    token = g.params["token"]
    user = Keychain.verify_auth_token(token)
    output = {}
    if user:
        #assegno il token alla sessione
        session["token"] = token
        s = Socket(user_id = user.id, socket_id = request.sid)
        db.session.add(s)
        db.session.commit()
        print "User %s just connected to socketio server." % user.username
        output = get_connection_values(user)
    output["success"] = user != None
    emit("auth", output)

@socketio.on("logout")
@ws_auth_required
def logout(data = None):
    # rimuovo il token se presente
    session.pop("token", None)
    emit("logout", {"success": session.get("token") == None})
    print "User disconnect from socket."
    disconnect() # chiude il socket, bisogna refreshare su socketio tester
