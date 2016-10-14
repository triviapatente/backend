from test.auth.http.api import register as register_user
from flask import json

def login(self, socket = None, token = None):
    if not token:
        token = self.token
    if not socket:
        socket = self.socket
    socket.emit("auth", {"token": token})
    return socket.get_received()

def logout(socket):
    socket.emit("logout")
    return socket.get_received()
