# -*- coding: utf-8 -*-

from app import socketio
from flask import request, g
from flask_socketio import emit
from app.message.utils import *
from app.game.models import Game
from app.decorators import needs_values
from app.ws_decorators import ws_auth_required, check_in_room

@socketio.on("send_message")
@ws_auth_required
@needs_values("SOCKET", "game_id", "content")
@check_in_room("game", "game_id")
def on_message(data):
    game = Game.query.filter_by(id = g.params["game_id"]).first()
    message = saveMessage(user = g.user, game = game, message = data["content"])
    if message:
        # send message to all in the room
        emit('send_message', {"success":True, "message": message.json}, room = g.roomName)
    else:
        emit('send_message_result', {"success": False})
