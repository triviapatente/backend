
from test.shared import TPAuthTestCase
from api import *
from tp.game.models import Category

class AuthSocketTestCase(TPAuthTestCase):

    def test_logout(self):

        print "#1: Token sbagliato"
        response = logout(self.socket, "fdsfsdf")
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 401

        print "#2: Token mancante"
        response = logout(self.socket, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 401

        print "#3: Successful logout"
        response = logout(self.socket, self.token)
        assert response.json.get("success") == True
