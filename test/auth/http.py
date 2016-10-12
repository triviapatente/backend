# -*- coding: utf-8 -*-

from test.utils import TPTestCase
from flask import json
from tp import app
import os, io
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

    def changeImage(self, token, image):
        response = self.app.post("account/image/edit", content_type='multipart/form-data', data = {"image": image}, headers = {"tp-session-token": token})
        response.json = json.loads(response.data)
        return response

    def getItalianRank(self, token):
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
        assert response.status_code == 403

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

    def test_changeImage(self):
        self.register("user", "user@gmail.com", "user")
        token = self.login("user", "user").json.get("token")

        validImage = (io.BytesIO(b'my file contents'), "image.jpg")
        invalidImage = (io.BytesIO(b'my file contents'), "image.exe")

        print "#1: Immagine non salvata se non valida"
        response = self.changeImage(token, invalidImage)
        assert response.status_code == 405

        print "#2: Immagine salvata correttamente se valida"
        response = self.changeImage(token, validImage)
        imagePath = response.json.get("user")["image"]
        assert response.status_code == 200 and imagePath

        print "#3: L'immagine salvata si chiama come il nome utente e si trova in %s" % app.config["UPLOAD_FOLDER"]
        assert imagePath == app.config["UPLOAD_FOLDER"] + "user.jpg"

        print "#4: L'immagine esiste nel folder"
        assert os.path.isfile(imagePath)


    def test_getItalianRank(self):
        number_of_results = app.config["RESULTS_LIMIT_RANK_ITALY"]
        MAX = number_of_results + 3
        for i in range (0, MAX):
            self.register("user%s" % i, "user%s@gmail.com" % i, "user%s" % i)
        token = self.login("user%s" % (MAX-1), "user%s" % (MAX-1)).json.get("token")

        print "#1: Classifica ricevuta correttamente"
        response = self.getItalianRank(token)
        assert response.status_code == 200

        rank = response.json.get("rank")
        print "#2: Classifica di %s elementi come predefinito" % number_of_results
        assert len(rank) == number_of_results

        # essendo il token dell'ultimo utente inserito, se è in classifica il metodo getRank funziona
        print "#3: User in classifica"
        exist = False
        for user_position in rank:
            if user_position["user"].get("username") == "user%s" % (MAX-1):
                exist = True
                break
        assert exist

        print "#4: La classifica è descrescente"
        last = None
        for user_position in rank:
            if last and last < user_position["user"].get("score"):
                assert False
            last = user_position["user"].get("score")

        # altri test non vale la pena farli perchè implicherebbero l'implementazione del metodo stesso
