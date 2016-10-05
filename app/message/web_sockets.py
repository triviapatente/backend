# -*- coding: utf-8 -*-

from app import socketio
from flask import request, json
from flask_socketio import emit, Namespace, join_room, leave_room
from app.message.utils import *
from app.auth.models import Keychain
from app.game.models import Game

# class-based namespace, the events have the "on_" prefix
class Chat(Namespace):
    # save the received message and response with True (message correctly received) or False (message not correctly received)
    def on_message(self, data):
        user = Keychain.verify_auth_token(data["user_token"])
        game = Game.query.filter_by(id = data["game_id"]).first()
        message = saveMessage(user = user, game = game, message = data["content"])
        if message:
            emit('message', json.dumps(message.json), room = data["game_id"])
        emit('response', False)
    def on_join_room(self, data):
        join_room(data["game_id"])
        emit("connection response", 'Connected', room = data["game_id"])
    def on_leave_room(self, data):
        leave_room(data["game_id"])
    # event triggered on connection
    def on_connect(self):
        # TODO auth stuff
        emit('connection response', "connected")
    def on_disconnect(self):
        print 'Client disconnected'
socketio.on_namespace(Chat('/chat'))
