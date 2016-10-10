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

    ###TEST METHODS###

    def test_register(self):
        print "#1: Registrazione corretta"
        response = self.register("2113145723", "2713345123@gmail.com", "dfsdvsv")
        assert response.status_code == 200
        assert response.json.get("user") and response.json.get("token")

        print "#2: Utente già esistente"
        response = self.register("123", "12@gmail.com", "dfsdvsv")
        assert response.status_code == 401
        error = response.json.get("message")
        print error
        assert error
        assert "Esiste già un utente con questo" in error

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

    #per creare un metodo di test basta mettere test_ prima del metodo
    def test_login(self):
        print "#1: Login corretto"
        response = self.login("2", "2")
        assert response.status_code == 200
        assert response.json.get("user") and response.json.get("token")

        print "#2: Username/email errata"
        response = self.login("a", "2")
        assert response.status_code == 401

        print "#3: Password errata"
        response = self.login("2", "a")
        assert response.status_code == 401

        print "#4: Coppia errata"
        response = self.login("a", "a")
        assert response.status_code == 401

        print "#4: Parametri mancanti"
        print "#4.1: username"
        response = self.login(None, "a")
        assert response.status_code == 400

        print "#4.1: password"
        response = self.login("a", None)
        assert response.status_code == 400
