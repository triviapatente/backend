# -*- coding: utf-8 -*-

from app import socketio
from flask_socketio import emit, Namespace
from app.message.utils import *
from app.auth.models import Keychain
from app.game.models import Game

# class-based namespace, the events have the "on_" prefix
class Chat(Namespace):
    # save the received message and response with True (message correctly received) or False (message not correctly received)
    def on_message(self, data):
        try:
            user = Keychain.verify_auth_token(data["user_token"])
            game = Game.query.filter_by(id = data["game_id"]).first()
            emit("result", saveMessage(user = user, game = game, message = data["content"]))
        except:
            emit("result", False)
    # event triggered on connection
    def on_connect(self):
        # TODO auth stuff
        emit('connection response', "connected")
    def on_disconnect(self):
        print 'Client disconnected'
socketio.on_namespace(Chat('/chat'))
