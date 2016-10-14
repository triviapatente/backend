# -*- coding: utf-8 -*-

def join_room(self, id, type):
    self.socket.emit("join_room", {"id": id, "type": type});
    return self.socket.get_received()

def leave_room(self, id, type):
    self.socket.emit("leave_room", {"id": id, "type": type});
    return self.socket.get_received()
