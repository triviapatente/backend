# -*- coding: utf-8 -*-

def join_room(socket, id, type):
    socket.emit("join_room", {"id": id, "type": type});
    return socket.get_received()

def leave_rooms(socket, type):
    socket.emit("leave_room", {"type": type});
    return socket.get_received()

def global_infos(socket, token):
    socket.emit("global_infos", {"tp-session-token": token})
