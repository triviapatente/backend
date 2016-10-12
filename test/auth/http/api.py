from flask import json

#Utility methods
def login(app, username, password):
    return app.post("/auth/login", data = {"user": username, "password": password})
def register(app, username, email, password):
    return app.post("/auth/register", data = {"username": username, "email": email, "password": password})

def logout(app, token):
    return app.post("/auth/logout", token = token)

def getCurrentUser(app, token):
    return app.get("/account/user", token = token)

def changeName(app, token, name):
    return app.post("account/name/edit", data = {"name": name}, token = token)

def changeSurname(app, token, surname):
    return app.post("account/surname/edit", data = {"surname": surname}, token = token)

def getItalianRank(app, token):
    return app.get("/info/rank/italy", token = token)

def changeImage(app, token, image):
    return app.post("account/image/edit", content_type='multipart/form-data', data = {"image": image}, token = token)
