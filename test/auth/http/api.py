from flask import json

def login(self, username, password):
    return self.app.post("/auth/login", data = {"user": username, "password": password})
def register(self, username, email, password):
    return self.app.post("/auth/register", data = {"username": username, "email": email, "password": password})

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

def changePassword(self, old, new, token = None):
    if not token:
        token = self.token
    return self.app.post("auth/password/edit", data = {"old_value": old, "new_value": new}, token = token)

def requestNewPassword(self, value):
    return self.app.post("auth/password/request", data = {"usernameOrEmail": value})

def changePasswordWebPage(self, token):
    suffix = ""
    if token:
        suffix = "?token=%s" % token
    return self.app.get("auth/password/change_from_email%s" % suffix)

def changePasswordWebPageResult(self, token, password):
    return self.app.post("auth/password/change_from_email", data = {"token": token, "password": password})
