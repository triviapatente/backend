# -*- coding: utf-8 -*-

def send_message(game_id, content, socket = None):
    if not socket:
        socket = self.socket
    socket.emit("send_message", {"game_id": game_id, "content": content})
    return socket.get_received()
