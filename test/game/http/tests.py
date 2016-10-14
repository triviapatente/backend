from api import *
from test.shared import TPAuthTestCase
from test.auth.http.api import register
class GameHTTPTestCase(TPAuthTestCase):

    first_opponent = None
    second_opponent = None
    third_opponent = None

    def setUp(self):
        super(GameHTTPTestCase, self).setUp()
        self.first_opponent = register(self, "test1", "test1@gmail.com", "test").json.get("user")
        self.second_opponent = register(self, "test2", "test2@gmail.com", "test").json.get("user")
        self.third_opponent = register(self, "test3", "test3@gmail.com", "test").json.get("user")


    def test_new_game(self):
        opponent_id = self.first_opponent.get("id")

        print "#1 creazione game"
        response = new_game(self, opponent_id)
        assert response.json.get("success") == True
        assert response.json.get("game")
        assert response.json.get("user")

        print "#2 creazione game con utente inesistente"
        response = new_game(self, 32)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#3 Parametri mancanti: utente"
        response = new_game(self, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

    def test_random_search(self):

        print "#1 creazione game"
        response = new_random_game(self)
        assert response.json.get("success") == True
        assert response.json.get("game")
        user1 = response.json.get("user")
        assert user1

        print "#2 creazione game"
        response = new_random_game(self)
        assert response.json.get("success") == True
        assert response.json.get("game")
        user2 = response.json.get("user")
        assert user2

        print "#3 creazione game"
        response = new_random_game(self)
        assert response.json.get("success") == True
        assert response.json.get("game")
        user3 = response.json.get("user")
        assert user3

        print "Opponents: ", user1.get("id"), user2.get("id"), user3.get("id")