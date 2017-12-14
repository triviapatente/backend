# -*- coding: utf-8 -*-
from flask import g, request
from tp import socketio, db
from tp.ws_decorators import ws_auth_required, filter_input_room
from tp.base.utils import roomName, get_connection_values, getInfosFromRoom
from tp.events.models import *
from tp.auth.utils import getUserFromRequest
from tp.events.models import Socket
from tp.decorators import needs_values
from flask_socketio import emit, join_room, leave_room, rooms
from flask import g, request
import events

@socketio.on("join_room")
@ws_auth_required
@needs_values("SOCKET", "id", "type")
@filter_input_room
def join_room_request(data):
    type = data.get("body").get("type")
    id = data.get("body").get("id")
    participation = RoomParticipation.query.filter(RoomParticipation.socket_id == request.sid, RoomParticipation.game_id == id).first()
    if not participation:
        participation = RoomParticipation(socket_id = request.sid, game_id = id, user_id = g.user.id)
        db.session.add(participation)
        db.session.commit()
        print "User %s joined room %s." % (g.user.username, g.roomName)
    leave_rooms(exceptGameId = id)
    emit("join_room", {"success": True})
    events.user_joined(g.roomName)


@socketio.on("global_infos")
@ws_auth_required
def get_global_infos(data):
    output = get_connection_values(g.user)
    output["success"] = True
    emit("global_infos", output)

@socketio.on("leave_room")
@ws_auth_required
@needs_values("SOCKET", "type")
@filter_input_room
def leave_room_request(data):
    #tipo di room (room di gioco, per esempio)
    type = data.get("body").get("type")
    leave_rooms()
    emit("leave_room", {"success": True})

def leaveRoomsQuery(exceptGameId):
    query = RoomParticipation.query.filter(RoomParticipation.user_id == g.user.id)
    if exceptGameId:
        query = query.filter(RoomParticipation.game_id != exceptGameId)
    return query

#elimina l'utente da tutte le room di un tipo (type), tranne la room di riferimento (actual_room)
def leave_rooms(exceptGameId = None):
    joinedRooms = leaveRoomsQuery(exceptGameId).all()
    for room in joinedRooms:
        name = "game_%s" % room.game_id
        print "User %s left room %s" % (g.user.username, name)
        events.user_left(name)
    leaveRoomsQuery(exceptGameId).delete()
    db.session.commit()

@socketio.on("disconnect")
def disconnect():
    print "About to be disconnected"
    g.user = getUserFromRequest(socket = True)
    print g.user.id
    if g.user:
        leave_rooms_for("game")
        Socket.query.filter(Socket.user_id == g.user.id).delete()
        db.session.commit()
        print "User %s has disconnected" % g.user.username
    else:
        print "Anonymous user has disconnected"
