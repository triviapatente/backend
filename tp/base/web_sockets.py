# -*- coding: utf-8 -*-
from flask import g, request
from tp import socketio
from tp.ws_decorators import ws_auth_required, filter_input_room
from tp.base.utils import roomName
from tp.decorators import needs_values
from flask_socketio import emit, join_room, leave_room, rooms
from flask import g
import events

@socketio.on("join_room")
@ws_auth_required
@needs_values("SOCKET", "id", "type")
@filter_input_room
def join_room_request(data):
    join_room(g.roomName)
    print "User %s joined room %s." % (g.user.username, g.roomName)
    emit("join_room", {"success": True})
    events.user_joined(g.roomName)

@socketio.on("leave_room")
@ws_auth_required
@needs_values("SOCKET", "id", "type")
@filter_input_room
def leave_room_request(data):
    #id della room (id del gioco, per esempio)
    id = data.get("id")
    #tipo di room (room di gioco, per esempio)
    type = data.get("type")
    #ottengo il nome della stanza
    name = roomName(id, type)
    if name in rooms():
        leave_room(name)
        events.user_left(name)
        print "User %s leaved room %s." % (g.user.username, name)
    emit("leave_room", {"success": True})

@socketio.on("connect")
def connect():
    print "Anonymous user just connected."

@socketio.on("disconnect")
def disconnect():
    print "User %s just disconnected." % g.user.username
