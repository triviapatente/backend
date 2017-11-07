from test.auth.http.api import register as register_user
from flask import json

def logout(socket):
    socket.emit("logout")
    return socket.get_received()
