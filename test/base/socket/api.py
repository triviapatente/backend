# -*- coding: utf-8 -*-

def join_room(socket, id, type):
    socket.emit("join_room", {"id": id, "type": type});
    return socket.get_received()

def leave_room(socket, id, type):
    socket.emit("leave_room", {"id": id, "type": type});
    return socket.get_received()
