# -*- coding: utf-8 -*-

def join_room(socket, id, type, token):
    socket.emit("join_room", {"tp-session-token": token, "body": {"id": id, "type": type}})
    return socket.get_received()

def leave_rooms(socket, type, token):
    socket.emit("leave_room", {"tp-session-token": token, "body": {"type": type}})
    return socket.get_received()

def global_infos(socket, token):
    socket.emit("global_infos", {"tp-session-token": token})
    return socket.get_received()
