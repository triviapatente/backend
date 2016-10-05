# -*- coding: utf-8 -*-
from flask import g
from app import socketio
from app.decorators import ws_auth_required
from flask_socketio import emit, join_room, leave_room

@ws_auth_required
@socketio.on("join")
#TODO: add decorator that checks for parameters
#TODO: make auth decorator work
#TODO: make decorators that checks if a user can join to a room
def join_room(self, data):
    id = data["id"]
    join_room(id)
    emit("join", {"success": True})

@ws_auth_required
@socketio.on("leave")
#TODO: add decorator that checks for parameters
#TODO: make auth decorator work
#TODO: add logic that verifies if the user is already in the room
def leave_room(self, data):
    id = data["id"]
    leave_room(id)
    emit("leave", {"success": True})

@socketio.on("connect")
def connect():
    print "Anonymous user just connected"

@socketio.on("disconnect")
def disconnect():
    print "User %s just disconnected" % g.user.username
