# -*- coding: utf-8 -*-

from app import socketio
from flask_socketio import send, emit
from app.decorators import auth_required

@socketio.on('my event', namespace='/test')
def handle_my_custom_namespace_event(message):
    emit('my response', "ciao")
