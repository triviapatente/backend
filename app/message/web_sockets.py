# -*- coding: utf-8 -*-

from app import socketio
from flask import request, json, g
from flask_socketio import emit, Namespace, join_room, leave_room
from app.message.utils import *
from app.game.models import Game
from app.decorators import needs_values
from app.ws_decorators import ws_auth_required

@socketio.on("send_message")
@ws_auth_required
@needs_values("SOCKET", "game_id", "content")

#TODO: add decorator that checks that the user is the correct room
def on_message(data):
    room = data["game_id"]
    game = Game.query.filter_by(id = room).first()
    message = saveMessage(user = g.user, game = game, message = data["content"])
    if message:
        emit('send_message', {"success": True, "message": message.json})
    else:
        emit('send_message', {"success": False})
