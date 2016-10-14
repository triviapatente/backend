# -*- coding: utf-8 -*-

def send_message(socket, game_id, content):
    socket.emit("send_message", {"game_id": game_id, "content": content})
    return socket.get_received()
