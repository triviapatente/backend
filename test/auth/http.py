# -*- coding: utf-8 -*-

from test.utils import TPTestCase
from flask import json
class AuthHTTPTestCase(TPTestCase):

    #Utility methods
    def login(self, username, password):
        response = self.app.post("/auth/login", data = {"user": username, "password": password})
        response.json = json.loads(response.data)
        return response
    def register(self, username, email, password):
        response = self.app.post("/auth/register", data = {"username": username, "email": email, "password": password})
        response.data = response.data.encode("utf-8")
        response.json = json.loads(response.data)
        return response

    def logout(self, token):
        response = self.app.post("/auth/logout", headers = {"tp-session-token":token})
        response.json = json.loads(response.data)
        return response

    def getCurrentUser(self, token):
        response = self.app.get("/account/user", headers = {"tp-session-token":token})
        response.json = json.loads(response.data)
        return response

    def changeName(self, token, name):
        response = self.app.post("account/name/edit", data = {"name": name}, headers = {"tp-session-token":token})
        response.json = json.loads(response.data)
        return response

    def changeSurname(self, token, surname):
        response = self.app.post("account/surname/edit", data = {"surname": surname}, headers = {"tp-session-token":token})
        response.json = json.loads(response.data)
        return response

    #TODO test change image

    def getItalianRank(token):
        response = self.app.get("/info/rank/italy", headers = {"tp-session-token":token})
        response.json = json.loads(response.data)
        return response

    ###TEST METHODS###
    #per creare un metodo di test basta mettere test_ prima del metodo

    def test_register(self):
        print "#1: Registrazione corretta"
        response = self.register("user", "user@gmail.com", "dfsdvsv")
        assert response.status_code == 200
        assert response.json.get("user") and response.json.get("token")

        print "#2: Utente già esistente"
        print "#2.1: per username"
        response = self.register("user", "12@gmail.com", "dfsdvsv")
        assert response.status_code == 401

        print "#2.2: per email"
        response = self.register("123", "user@gmail.com", "dfsdvsv")
        assert response.status_code == 401

        print "#3: Parametri mancanti"

        print "#3.1: username"
        response = self.register(None, "wsdr@gmail.com", "dfsdvsv")
        assert response.status_code == 400

        print "#3.2: email"
        response = self.register("aisdisdf", None, "dfsdvsv")
        assert response.status_code == 400

        print "#3.3: password"
        response = self.register("aisdisdf", "wsdr@gmail.com", None)
        assert response.status_code == 400

        print "#4: Token valido"
        response = self.register("token", "token@gmail.com", "token")
        response = self.getCurrentUser(response.json.get("token"))
        assert response.status_code == 200

    def test_login(self):
        #chiamata propedeutica
        self.register("user", "user@gmail.com", "user")

        print "#1: Login corretto"
        response = self.login("user", "user")
        assert response.status_code == 200
        assert response.json.get("user") and response.json.get("token")

        print "#2: Username/email errata"
        response = self.login("a", "user")
        assert response.status_code == 401

        print "#3: Password errata"
        response = self.login("user", "a")
        assert response.status_code == 401

        print "#4: Coppia errata"
        response = self.login("a", "a")
        assert response.status_code == 401

        print "#4: Parametri mancanti"
        print "#4.1: username"
        response = self.login(None, "user")
        assert response.status_code == 400

        print "#4.1: password"
        response = self.login("user", None)
        assert response.status_code == 400

        print "#5: Token valido"
        response = self.login("user", "user")
        response = self.getCurrentUser(response.json.get("token"))
        assert response.status_code == 200

    def test_getCurrentUser(self):
        self.register("user", "user@gmail.com", "user")
        token = self.login("user", "user").json.get("token")

        print "#1: Accesso possibile con token valido"
        response = self.getCurrentUser(token)
        assert response.status_code == 200

        print "#2: Accesso negato con token non valido"
        response = self.getCurrentUser("INVALID_TOKEN")
        assert response.status_code != 200

    def test_logout(self):
        self.register("user", "user@gmail.com", "user")
        token = self.login("user", "user").json.get("token")

        print "#1: Logout corretto"
        response = self.logout(token)
        assert response.status_code == 200

        print "#2: Impossibile accedere con lo stesso token"
        response = self.getCurrentUser(token)
        assert response.status_code == 403

    def test_changeName(self):
        self.register("user", "user@gmail.com", "user")
        token = self.login("user", "user").json.get("token")

        print "#1: Cambio di nome effettuato"
        response = self.changeName(token, "name")
        assert response.status_code == 200 and response.json.get("user").get("name") == "name"

    def test_changeSurname(self):
        self.register("user", "user@gmail.com", "user")
        token = self.login("user", "user").json.get("token")

        print "#1: Cambio di cognome effettuato"
        response = self.changeSurname(token, "surname")
        assert response.status_code == 200 and response.json.get("user").get("surname") == "surname"

    # TODO test get rank e change image
