# -*- coding: utf-8 -*-

from app import socketio
from flask_socketio import emit, Namespace
import json

# class-based namespace, the events have the "on_" prefix
class Chat(Namespace):
    def on_message(self, message):
        try:
            emit("message", message["id"])
        except Exception as e:
            emit("message", str(e))
    # event triggered on connection
    def on_connect(self):
        # TODO auth stuff
        emit('connection response', "connected")
    def on_disconnect(self):
        print 'Client disconnected'
socketio.on_namespace(Chat('/chat'))
