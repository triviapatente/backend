# -*- coding: utf-8 -*-

from tp import socketio
from flask import session, g, request
from flask_socketio import emit, disconnect
from models import Keychain
from tp import db
from tp.events.models import Socket
from tp.decorators import needs_values, track_time
from tp.ws_decorators import ws_auth_required


@socketio.on("logout")
@ws_auth_required
def logout(data = None):
    emit("logout", {"success": True})
    disconnect() # chiude il socket, bisogna refreshare su socketio tester
