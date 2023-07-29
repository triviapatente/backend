# -*- coding: utf-8 -*-
from flask import g
from flask_socketio import emit

from tp import socketio, db
from tp.ws_decorators import ws_auth_required, filter_input_room
from tp.base.utils import roomName, get_connection_values, getInfosFromRoom
from tp.base import events
from tp.events.models import *
from tp.auth.utils import getUserFromRequest, deviceIdFromRequest, unsetToken, unsetDeviceId
from tp.events.models import Socket
from tp.decorators import create_session
from tp.decorators import needs_values

@socketio.on("join_room")
@create_session
@ws_auth_required
@needs_values("SOCKET", "id", "type")
@filter_input_room
def join_room_request(data):
    room_type = g.params.get("type")
    room_id = g.params.get("id")
    participation = RoomParticipation.query.filter(RoomParticipation.game_id == room_id, RoomParticipation.user_id == g.user.id, RoomParticipation.device_id == g.deviceId).first()
    if not participation:
        participation = RoomParticipation(game_id = room_id, user_id = g.user.id, device_id = g.deviceId)
        db.session.add(participation)
        db.session.commit()
    print(f"User {g.user.username} joined room {g.roomName}. (deviceId = {g.deviceId})")
    emit("join_room", {"success": True})
    leave_rooms(exceptId = room_id)
    events.user_joined(g.roomName)

@socketio.on("global_infos")
@create_session
@ws_auth_required
def get_global_infos(data):
    output = get_connection_values(g.user)
    output["success"] = True
    emit("global_infos", output)

@socketio.on("leave_room")
@create_session
@ws_auth_required
@needs_values("SOCKET", "type")
@filter_input_room
def leave_room_request(data):
    #tipo di room (room di gioco, per esempio)
    leave_rooms()
    emit("leave_room", {"success": True})

def leaveRoomsQuery(exceptId):
    query = RoomParticipation.query.filter(RoomParticipation.device_id == g.deviceId)
    if exceptId:
        query = query.filter(RoomParticipation.game_id != exceptId)
    return query

#elimina l'utente da tutte le room di un tipo (type), tranne la room di riferimento (actual_room)
def leave_rooms(exceptId = None):
    joinedRooms = leaveRoomsQuery(exceptId).all()
    roomIds = [room.game_id for room in joinedRooms]
    leaveRoomsQuery(exceptId).delete()
    db.session.commit()
    for game_id in roomIds:
        name = "game_%s" % game_id
        print(f"User {g.user.username} left room {name}")
        events.user_left(name)

@socketio.on("disconnect")
@create_session
def disconnect():
    print("About to be disconnected")
    g.user = getUserFromRequest(socket = True)
    g.deviceId = deviceIdFromRequest()
    if g.user and g.deviceId:
        leave_rooms()
        Socket.query.filter(Socket.device_id == g.deviceId).delete()
        db.session.commit()
        print(f"User {g.user.username} has disconnected")
    else:
        print("Anonymous user has disconnected")
    unsetDeviceId()
    unsetToken()
