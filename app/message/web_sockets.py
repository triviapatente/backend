# -*- coding: utf-8 -*-

from app import socketio
from flask_socketio import emit, Namespace
from app.decorators import auth_required_ws

from flask import g

# class-based namespace, the events have the "on_" prefix
@auth_required_ws
class Chat(Namespace):
    def on_message(self, message):
        emit('message', message)
    # event triggered on connection
    def on_connect(self):
        emit('connection response', {'data': 'Connected', 'User': g.user.username })
    def on_disconnect(self):
        print 'Client disconnected'
#socketio.on_namespace(Chat('/chat'))
