from test.auth.http.api import register as register_user
from flask import json

def login(socket, token):
    socket.emit("auth", {"token": token})
    response = socket.get_received()
    assert len(response)
    args = response[0].get("args")
    json = args[0]
    assert json
    output = lambda: None
    output.json = json
    return output

def logout(socket):
    socket.emit("logout")
    response = socket.get_received()
    assert len(response)
    args = response[0].get("args")
    json = args[0]
    assert json
    output = lambda: None
    output.json = json
    return output

def register(app, username, email, password):
    response = register_user(app, username, email, password)
    return response.json.get("token")
