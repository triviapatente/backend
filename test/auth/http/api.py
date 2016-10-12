from flask import json

#Utility methods
def login(app, username, password):
    response = app.post("/auth/login", data = {"user": username, "password": password})
    response.json = json.loads(response.data)
    return response
def register(app, username, email, password):
    response = app.post("/auth/register", data = {"username": username, "email": email, "password": password})
    response.data = response.data.encode("utf-8")
    response.json = json.loads(response.data)
    return response

def logout(app, token):
    response = app.post("/auth/logout", headers = {"tp-session-token":token})
    response.json = json.loads(response.data)
    return response

def getCurrentUser(app, token):
    response = app.get("/account/user", headers = {"tp-session-token":token})
    response.json = json.loads(response.data)
    return response

def changeName(app, token, name):
    response = app.post("account/name/edit", data = {"name": name}, headers = {"tp-session-token":token})
    response.json = json.loads(response.data)
    return response

def changeSurname(app, token, surname):
    response = app.post("account/surname/edit", data = {"surname": surname}, headers = {"tp-session-token":token})
    response.json = json.loads(response.data)
    return response

def getItalianRank(app, token):
    response = app.get("/info/rank/italy", headers = {"tp-session-token":token})
    response.json = json.loads(response.data)
    return response

def changeImage(app, token, image):
    response = app.post("account/image/edit", content_type='multipart/form-data', data = {"image": image}, headers = {"tp-session-token": token})
    response.json = json.loads(response.data)
    return response
