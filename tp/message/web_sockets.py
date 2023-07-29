# -*- coding: utf-8 -*-

from tp import socketio
from flask import request, g
from flask_socketio import emit
from tp.message.utils import *
from tp.game.models import Game
from tp.decorators import needs_values
from tp.ws_decorators import ws_auth_required, check_in_room
from tp.base.utils import RoomType
from tp.decorators import create_session
from tp.message.events import send_message

@socketio.on("send_message")
@create_session
@ws_auth_required
@needs_values("SOCKET", "game_id", "content")
@check_in_room(RoomType.game, "game_id")
def on_message(data):
    game = Game.query.filter_by(id = g.params["game_id"]).first()
    message = saveMessage(user = g.user, game = game, message = data["content"])
    if message:
        # send message to all in the room
        print(f"User {g.user.username} sent message to room {g.roomName}:", message.json)
        emit('send_message', {"success":True, "message": message.json})
        send_message(g.roomName, message)
    else:
        print(f"User {g.user.username} unable to sent message.")
        emit('send_message', {"success": False})
