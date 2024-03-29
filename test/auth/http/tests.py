# -*- coding: utf-8 -*-

import io, os

from flask import json
from tp import app
from tp.auth.models import Keychain
from test.shared import TPTestCase
from test.auth.http.api import *

class AuthHTTPTestCase(TPTestCase):
    def test_register(self):
        print("#1: Registrazione corretta")
        response = register(self, "user", "user@gmail.com", "dfsdsdfvsv")
        assert response.status_code == 200
        assert response.json.get("user") and response.json.get("token")

        print("#2: Utente già esistente")
        print("#2.1: per username")
        response = register(self, "user", "12@gmail.com", "dfsdsdfvsv")
        assert response.status_code == 403

        print("#2.2: per email")
        response = register(self, "123", "user@gmail.com", "dfsdsdfvsv")
        assert response.status_code == 403

        print("#2.3: per username (case insensitive)")
        response = register(self, "User", "12@gmail.com", "dfsdsdfvsv")
        assert response.status_code == 403

        print("#2.4: per email (case insensitive)")
        response = register(self, "123", "User@gmail.com", "dfsdsdfvsv")
        assert response.status_code == 403

        print("#3: Parametri mancanti")

        print("#3.1: username")
        response = register(self, None, "wsdr@gmail.com", "dfsdsdfvsv")
        assert response.status_code == 400

        print("#3.2: email")
        response = register(self, "aisdisdf", None, "dfsdsdfvsv")
        assert response.status_code == 400

        print("#3.3: password")
        response = register(self, "aisdisdf", "wsdr@gmail.com", None)
        assert response.status_code == 400

        print("#4: Token valido")
        response = register(self, "token", "token@gmail.com", "dfsdsdfvsv")
        response = getCurrentUser(self, response.json.get("token"))
        assert response.status_code == 200

        print("#5: Stringa vuota nella richiesta")
        response = register(self, "", "", "")
        assert response.status_code == 400

        print("#6: No spazi nell'username")
        response = register(self, "1 2", "sdf@sdf.it", "sdfdsfsdf")
        assert response.status_code == 400
        print("#7: No spazi nell'email")
        response = register(self, "12", "sdf @sdf.it", "sdfdsfsdf")
        assert response.status_code == 400

        print("#8: Email non valida")
        response = register(self, "123", "123.it", "dfsdsdfvsv")
        assert response.status_code == 400
        response = register(self, "123", "123@.it", "dfsdsdfvsv")
        assert response.status_code == 400
        response = register(self, "123", "@df.it", "dfsdsdfvsv")
        assert response.status_code == 400

        print("#9: username non valido")
        response = register(self, "12", "sdf@sdf.it", "sdfdsfsdf")
        assert response.status_code == 400
        print("#10: password non valida")
        response = register(self, "12asdsd", "sdf@sddf.it", "asd")
        assert response.status_code == 400

        print("#11: Strip")
        print("#11.1 username")
        response = register(self, " token ", "sdf@sddf.it", "asd")
        assert response.status_code == 403
        print("#11.1 email")
        response = register(self, "tokensad", " token@gmail.com ", "asd")
        assert response.status_code == 403


    def test_login(self):
        #chiamata propedeutica
        register(self, "user", "user@gmail.com", "usesdfsdfr")

        print("#1: Login corretto")
        response = login(self, "user", "usesdfsdfr")
        assert response.status_code == 200
        assert response.json.get("user") and response.json.get("token")

        print("#1.1: Login corretto case insensitive")
        response = login(self, "User", "usesdfsdfr")
        assert response.status_code == 200
        assert response.json.get("user") and response.json.get("token")

        print("#2: Username/email errata")
        response = login(self, "a23423", "usesdfsdfr")
        assert response.status_code == 400

        print("#3: Password errata")
        response = login(self, "user", "a")
        assert response.status_code == 400

        print("#4: Coppia errata")
        response = login(self, "a234234", "234234a")
        assert response.status_code == 400

        print("#4: Parametri mancanti")
        print("#4.1: username")
        response = login(self, None, "usesdfsdfr")
        assert response.status_code == 400

        print("#4.1: password")
        response = login(self, "user", None)
        assert response.status_code == 400

        print("#5: Token valido")
        response = login(self, "user", "usesdfsdfr")
        user_response = getCurrentUser(self, response.json.get("token"))
        assert user_response.status_code == 200

        print("#6 In due chiamate differenti, i token coincidono")
        response2 = login(self, "user", "usesdfsdfr")
        assert response2.status_code == 200
        assert response.json.get("token") == response2.json.get("token")

        print("#7: Strip")
        print("#7.1 username")
        response = login(self, " user ", "usesdfsdfr")
        assert response.status_code == 200
        print("#7.1 email")
        response = login(self, " user@gmail.com ", "usesdfsdfr")
        assert response.status_code == 200

    def test_changeName(self):
        token = register(self, "user", "user@gmail.com", "ussdfsdfer").json.get("token")

        print("#1: Cambio di nome effettuato")
        response = changeName(self, "name", token)
        assert response.status_code == 200 and response.json.get("user").get("name") == "name"

        print("#2: Cambio di nome: trimming spazi")
        response = changeName(self, "   name     ", token)
        assert response.status_code == 200 and response.json.get("user").get("name") == "name"

        print("#3: Cambio di nome: stringa vuota")
        response = changeName(self, "", token)
        assert response.status_code == 200 and response.json.get("user").get("name") is None

        print("#4: Cambio di nome: stringa solo spazi")
        response = changeName(self, "  ", token)
        assert response.status_code == 200 and response.json.get("user").get("name") is None

    def test_changeSurname(self):
        token = register(self, "user", "user@gmail.com", "sdfsdfsdfssf").json.get("token")

        print("#1: Cambio di cognome effettuato")
        response = changeSurname(self, "surname", token)
        assert response.status_code == 200 and response.json.get("user").get("surname") == "surname"

        print("#2: Cambio di cognome: trimming spazi")
        response = changeSurname(self, "   surname     ", token)
        assert response.status_code == 200 and response.json.get("user").get("surname") == "surname"

        print("#3: Cambio di cognome: stringa vuota")
        response = changeSurname(self, "", token)
        assert response.status_code == 200 and response.json.get("user").get("surname") is None

        print("#4: Cambio di cognome: stringa solo spazi")
        response = changeSurname(self, "  ", token)
        assert response.status_code == 200 and response.json.get("user").get("surname") is None

    def test_changeImage(self):
        token = register(self, "user", "user@gmail.com", "sdfdsfsdf").json.get("token")

        validImage = (io.BytesIO(b'my file contents'), "image.jpg")
        invalidImage = (io.BytesIO(b'my file contents'), "image.exe")

        print("#1: Immagine non salvata se non valida")
        response = changeImage(self, invalidImage, token)
        assert response.status_code == 405

        print("#2: Immagine salvata correttamente se valida")
        response = changeImage(self, validImage, token)
        imagePath = response.json.get("user")["image"]
        assert response.status_code == 200 and imagePath

        print(f"#3: L'immagine salvata si chiama come il nome utente e si trova in {app.config['UPLOAD_FOLDER']}")
        assert imagePath == app.config["UPLOAD_FOLDER"] + "user.jpg"

        print("#4: L'immagine esiste nel folder")
        assert os.path.isfile(imagePath)

    def test_getCurrentUser(self):
        token = register(self, "user", "user@gmail.com", "sdfsdfsdfsdfsdf").json.get("token")

        print("#1: Accesso possibile con token valido")
        response = getCurrentUser(self, token)
        assert response.status_code == 200

        print("#2: Accesso negato con token non valido")
        response = getCurrentUser(self, "INVALID_TOKEN")
        assert response.status_code == 401

    def test_change_password(self):
        password = "sdfsdfsdfsdf"
        token = register(self, "user", "user@gmail.com", password).json.get("token")

        print("#1: Password precedente non combaciante")
        response = changePassword(self, "dfsf", "fjfjfjfjfj", token)
        assert response.status_code == 403

        print("#2: Password cambiata con successo")
        response = changePassword(self, password, "fjfjfjfjfj", token)
        assert response.status_code == 200
        new_token = response.json.get("token")
        assert new_token

        print("#2.1: Accesso non consentito con vecchio token")
        response = getCurrentUser(self, token)
        assert response.status_code == 401

        print("#2.2: Accesso consentito con nuovo token")
        response = getCurrentUser(self, new_token)
        assert response.status_code == 200

        print("#3: Parametri mancanti")
        print("#3.1 old_password")
        response = changePassword(self, None, "fjfjfjfjfj", new_token)
        assert response.status_code == 400

        print("#3.2 new_password")
        response = changePassword(self, "fjfjfjfjfj", None, new_token)
        assert response.status_code == 400

        print("#4 password non valida")
        response = changePassword(self, "fjfjfjfjfj", "sdf", new_token)
        assert response.status_code == 400


    def test_request_new_password(self):
        #registrazione iniziale
        response = register(self, "user", "user@gmail.com", "dfsdvsv")
        user = response.json.get("user")

        print("#1: Username presente in db")
        username = user.get("username")
        response = requestNewPassword(self, username)
        assert response.status_code == 200

        print("#1.1 Username presente in db: case insensitive")
        username = username.title()
        response = requestNewPassword(self, username)
        assert response.status_code == 200

        print("#2: Email presente in db")
        email = user.get("email")
        response = requestNewPassword(self, email)
        assert response.status_code == 200

        print("#2.2 Email presente in db: case insensitive")
        email = email.title()
        response = requestNewPassword(self, email)
        assert response.status_code == 200

        print("#2: Username/email non presente in db")
        username = "dsfsdfsdf"
        response = requestNewPassword(self, username)
        assert response.status_code == 404

        print("#3: Parametri mancanti")
        print("#3.1: usernameOrEmail")
        response = requestNewPassword(self, None)
        assert response.status_code == 400

        print("#4: Strip")
        print("#4.1 username")
        username = " " + user.get("username") + " "
        response = requestNewPassword(self, username)
        assert response.status_code == 200
        print("#4.1 email")
        email = " " + user.get("email") + " "
        response = requestNewPassword(self, email)
        assert response.status_code == 200

    def test_change_password_webpage(self):
        #registrazione iniziale
        response = register(self, "user", "user@gmail.com", "dfsdvsv")
        user_id = response.json.get("user").get("id")

        print("#1: Richiesta successful")
        #ottengo il token giusto per l'utente
        keychain = Keychain.query.filter(Keychain.user_id == user_id).first()
        token = keychain.change_password_token

        response = changePasswordWebPage(self, token)
        assert response.status_code == 200

        print("#2: Parametri mancanti")
        print("#2.1: token")
        response = changePasswordWebPage(self, None)
        assert response.status_code == 400

    def test_change_password_webpage_result(self):

        #registrazione iniziale
        response = register(self, "user", "user@gmail.com", "dfsdvsv")
        user_id = response.json.get("user").get("id")

        print("#1: Token presente in db")
        #ottengo il token giusto per l'utente
        keychain = Keychain.query.filter(Keychain.user_id == user_id).first()
        token = keychain.change_password_token

        response = changePasswordWebPageResult(self, token, "fuffafuffa")
        assert response.status_code == 200

        print("#2: Token invalidato, e quindi non presente in db")

        response = changePasswordWebPageResult(self, token, "fuffafuffa")
        assert response.status_code == 403

        print("#3: Parametri mancanti")
        print("#3.1: token")
        response = changePasswordWebPageResult(self, None, "fuffafuffa")
        assert response.status_code == 400

        print("#3.2: password")
        response = changePasswordWebPageResult(self, "dsf", None)
        assert response.status_code == 400
