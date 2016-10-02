# -*- coding: utf-8 -*-

from app import socketio
from flask_socketio import emit, Namespace
import json

# class-based namespace, the events have the "on_" prefix
class Chat(Namespace):
    def on_message(self, message):
        emit('message', "message2")
        # message = json.loads(message)
        # emit('message', "message2")
    # event triggered on connection
    def on_connect(self):
        emit('connection response', "connected")
    def on_disconnect(self):
        print 'Client disconnected'

socketio.on_namespace(Chat('/chat'))
