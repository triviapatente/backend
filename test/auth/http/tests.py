# -*- coding: utf-8 -*-

from test.shared import TPTestCase
from flask import json
from api import *
from tp import app
import io, os

class AuthHTTPTestCase(TPTestCase):
    def test_register(self):
        print "#1: Registrazione corretta"
        response = register(self, "user", "user@gmail.com", "dfsdvsv")
        assert response.status_code == 200
        assert response.json.get("user") and response.json.get("token")

        print "#2: Utente già esistente"
        print "#2.1: per username"
        response = register(self, "user", "12@gmail.com", "dfsdvsv")
        assert response.status_code == 401

        print "#2.2: per email"
        response = register(self, "123", "user@gmail.com", "dfsdvsv")
        assert response.status_code == 401

        print "#3: Parametri mancanti"

        print "#3.1: username"
        response = register(self, None, "wsdr@gmail.com", "dfsdvsv")
        assert response.status_code == 400

        print "#3.2: email"
        response = register(self, "aisdisdf", None, "dfsdvsv")
        assert response.status_code == 400

        print "#3.3: password"
        response = register(self, "aisdisdf", "wsdr@gmail.com", None)
        assert response.status_code == 400

        print "#4: Token valido"
        response = register(self, "token", "token@gmail.com", "token")
        response = getCurrentUser(self, response.json.get("token"))
        assert response.status_code == 200

        print "#5: Stringa vuota nella richiesta"
        response = register(self, "", "", "")
        assert response.status_code == 400

    def test_login(self):
        #chiamata propedeutica
        register(self, "user", "user@gmail.com", "user")

        print "#1: Login corretto"
        response = login(self, "user", "user")
        assert response.status_code == 200
        assert response.json.get("user") and response.json.get("token")

        print "#2: Username/email errata"
        response = login(self, "a", "user")
        assert response.status_code == 401

        print "#3: Password errata"
        response = login(self, "user", "a")
        assert response.status_code == 401

        print "#4: Coppia errata"
        response = login(self, "a", "a")
        assert response.status_code == 401

        print "#4: Parametri mancanti"
        print "#4.1: username"
        response = login(self, None, "user")
        assert response.status_code == 400

        print "#4.1: password"
        response = login(self, "user", None)
        assert response.status_code == 400

        print "#5: Token valido"
        response = login(self, "user", "user")
        response = getCurrentUser(self, response.json.get("token"))
        assert response.status_code == 200

    def test_logout(self):
        register(self, "user", "user@gmail.com", "user")
        token = login(self, "user", "user").json.get("token")

        print "#1: Logout corretto"
        response = logout(self, token)
        assert response.status_code == 200

        print "#2: Impossibile accedere con lo stesso token"
        response = getCurrentUser(self, token)
        assert response.status_code == 403

    def test_changeName(self):
        register(self, "user", "user@gmail.com", "user")
        token = login(self, "user", "user").json.get("token")

        print "#1: Cambio di nome effettuato"
        response = changeName(self, "name", token)
        assert response.status_code == 200 and response.json.get("user").get("name") == "name"

    def test_changeSurname(self):
        register(self, "user", "user@gmail.com", "user")
        token = login(self, "user", "user").json.get("token")

        print "#1: Cambio di cognome effettuato"
        response = changeSurname(self, "surname", token)
        assert response.status_code == 200 and response.json.get("user").get("surname") == "surname"

    def test_changeImage(self):
        register(self, "user", "user@gmail.com", "user")
        token = login(self, "user", "user").json.get("token")

        validImage = (io.BytesIO(b'my file contents'), "image.jpg")
        invalidImage = (io.BytesIO(b'my file contents'), "image.exe")

        print "#1: Immagine non salvata se non valida"
        response = changeImage(self, invalidImage, token)
        assert response.status_code == 405

        print "#2: Immagine salvata correttamente se valida"
        response = changeImage(self, validImage, token)
        imagePath = response.json.get("user")["image"]
        assert response.status_code == 200 and imagePath

        print "#3: L'immagine salvata si chiama come il nome utente e si trova in %s" % app.config["UPLOAD_FOLDER"]
        assert imagePath == app.config["UPLOAD_FOLDER"] + "user.jpg"

        print "#4: L'immagine esiste nel folder"
        assert os.path.isfile(imagePath)

    def test_getCurrentUser(self):
        register(self, "user", "user@gmail.com", "user")
        token = login(self, "user", "user").json.get("token")

        print "#1: Accesso possibile con token valido"
        response = getCurrentUser(self, token)
        assert response.status_code == 200

        print "#2: Accesso negato con token non valido"
        response = getCurrentUser(self, "INVALID_TOKEN")
        assert response.status_code == 403

    
