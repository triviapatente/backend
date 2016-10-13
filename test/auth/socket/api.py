from test.auth.http.api import register as register_user
from flask import json

def login(self, token):
    self.socket.emit("auth", {"token": token})
    return self.socket.get_received()

def logout(self):
    self.socket.emit("logout")
    return self.socket.get_received()

def register(self, username, email, password):
    response = register_user(self, username, email, password)
    return response.json.get("token")
