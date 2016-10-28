
from test.shared import TPAuthTestCase
from api import *

class AuthSocketTestCase(TPAuthTestCase):
    def test_login(self):
        print "#1: Successful login"
        response = login(self)
        print(response)
        assert response.json.get("invites") is not None
        assert response.json.get("global_rank_position") is not None
        #TODO: assert response.json.get("friends_rank_position") is not None
        #TODO: assert response.json.get("stats") is not None

    def test_logout(self):
        response = login(self)

        print "#1: Successful logout"
        response = logout(self.socket)
        assert response.json.get("success") == True
