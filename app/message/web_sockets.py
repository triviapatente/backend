# -*- coding: utf-8 -*-

from app import socketio
from flask import request, json, g
from flask_socketio import emit, Namespace, join_room, leave_room
from app.message.utils import *
from app.game.models import Game
from app.decorators import ws_auth_required

@socketio.on("send_message")
@ws_auth_required
#TODO: add decorator that checks for parameters
#TODO: make auth decorator work
#TODO: add decorator that checks that the user is the correct room
def on_message(data):
    room = data["game_id"]
    game = Game.query.filter_by(id = room).first()
    message = saveMessage(user = g.user, game = game, message = data["content"])
    if message:
        emit('send_message', {"success": True, "message": message.json})
    else:
        emit('send_message', {"success": False})
