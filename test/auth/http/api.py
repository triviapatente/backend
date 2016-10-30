from flask import json

def login(self, username, password):
    return self.app.post("/auth/login", data = {"user": username, "password": password})
def register(self, username, email, password):
    return self.app.post("/auth/register", data = {"username": username, "email": email, "password": password})

def logout(self, token = None):
    if not token:
        token = self.token
    return self.app.post("/auth/logout", token = token)

def getCurrentUser(self, token = None):
    if not token:
        token = self.token
    return self.app.get("/account/user", token = token)

def changeName(self, name, token = None):
    if not token:
        token = self.token
    return self.app.post("account/name/edit", data = {"name": name}, token = token)

def changeSurname(self, surname, token):
    if not token:
        token = self.token
    return self.app.post("account/surname/edit", data = {"surname": surname}, token = token)

def changeImage(self, image, token = None):
    if not token:
        token = self.token
    return self.app.post("account/image/edit", content_type='multipart/form-data', data = {"image": image}, token = token)
