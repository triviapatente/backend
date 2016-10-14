from test.auth.http.api import register as register_user
from flask import json

def login(self, token = None):
    if not token:
        token = self.token
    self.socket.emit("auth", {"token": token})
    return self.socket.get_received()

def logout(self):
    self.socket.emit("logout")
    return self.socket.get_received()
