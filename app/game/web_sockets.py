# -*- coding: utf-8 -*-

from app import socketio

@socketio.on('my event', namespace='/test')
def handle_my_custom_namespace_event(json):
    print "hello world"
