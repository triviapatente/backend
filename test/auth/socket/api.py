from test.auth.http.api import register as register_user
from flask import json

def login(self, token):
    self.socket.emit("auth", {"token": token})
    response = self.socket.get_received()
    assert len(response)
    args = response[0].get("args")
    json = args[0]
    assert json
    output = lambda: None
    output.json = json
    return output

def logout(self):
    self.socket.emit("logout")
    response = self.socket.get_received()
    assert len(response)
    args = response[0].get("args")
    json = args[0]
    assert json
    output = lambda: None
    output.json = json
    return output

def register(self, username, email, password):
    response = register_user(self, username, email, password)
    return response.json.get("token")
