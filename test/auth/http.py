
from test.utils import TPTestCase
from flask import json
class AuthHTTPTestCase(TPTestCase):
    
    def login(self, username, password):
        response = self.app.post("/auth/login", data = {"user": username, "password": password})
        response.json = json.loads(response.data)
        return response

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

        print "#5: Username mancante"
        response = self.login(None, "a")
        assert response.status_code == 400

        print "#6: Password mancante"
        response = self.login("a", None)
        assert response.status_code == 400
