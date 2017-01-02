# -*- coding: utf-8 -*-
from flask import g, request
from tp import socketio, db
from tp.ws_decorators import ws_auth_required, filter_input_room
from tp.base.utils import roomName
from tp.auth.utils import getUserFromRequest
from tp.events.models import Socket
from tp.decorators import needs_values
from flask_socketio import emit, join_room, leave_room, rooms
from flask import g
import events

@socketio.on("join_room")
@ws_auth_required
@needs_values("SOCKET", "id", "type")
@filter_input_room
def join_room_request(data):
    type = data.get("type")
    join_room(g.roomName)
    print "User %s joined room %s." % (g.user.username, g.roomName)
    emit("join_room", {"success": True})
    events.user_joined(g.roomName)
    leave_rooms_for(type, g.roomName)

@socketio.on("leave_room")
@ws_auth_required
@needs_values("SOCKET", "type")
@filter_input_room
def leave_room_request(data):
    #tipo di room (room di gioco, per esempio)
    type = data.get("type")
    leave_rooms_for(type)
    emit("leave_room", {"success": True})


#elimina l'utente da tutte le room di un tipo (type), tranne la room di riferimento (actual_room)
def leave_rooms_for(type, actual_room = None):
    for name in rooms():
        if name != actual_room and name.startswith(type):
            leave_room(name)
            events.user_left(name)
            print "User %s left room %s." % (g.user.username, name)

@socketio.on("connect")
def connect():
    print "Anonymous user just connected."

@socketio.on("disconnect")
def disconnect():
    g.user = getUserFromRequest(socket = True)
    if g.user:
        leave_rooms_for("game")
        Socket.query.filter(Socket.user_id == g.user.id).delete()
        db.session.commit()
        print "User %s has disconnected" % g.user.username
    else:
        print "Anonymous user has disconnected"
