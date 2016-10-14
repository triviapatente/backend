
from test.shared import TPTestCase
from api import *
class AuthSocketTestCase(TPTestCase):
    #TEST METHODS

    def test_login(self):
        token = register(self, "pippo", "pippo@gmail.com", "pippo")

        response = login(self, token)
        assert response.json.get("success") == True

    def test_logout(self):
        token = register(self, "pippo", "pippo@gmail.com", "pippo")
        response = login(self, token)
        assert response.json.get("success") == True
        response = logout(self)
        assert response.json.get("success") == True
