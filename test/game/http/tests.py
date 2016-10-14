from api import *
from test.shared import TPAuthTestCase
from test.auth.http.api import register
class GameHTTPTestCase(TPAuthTestCase):

    first_opponent = None
    second_opponent = None
    third_opponent = None

    def setUp(self):
        super(GameHTTPTestCase, self).setUp()
        self.first_opponent = register(self, "test1", "test1@gmail.com", "test").json
        self.second_opponent = register(self, "test2", "test2@gmail.com", "test").json
        self.third_opponent = register(self, "test3", "test3@gmail.com", "test").json


    def test_new_game(self):
        opponent_id = self.first_opponent.get("user").get("id")

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

    def test_get_pending_invites(self):
        #ottengo id e token dell'opponent del quale voglio vedere gli inviti
        opponent_id = self.first_opponent.get("user").get("id")
        opponent_token = self.first_opponent.get("token")

        print "#1 ottengo gli inviti, con 0 inviti"
        response = get_pending_invites(self, opponent_token)
        assert response.json.get("success") == True
        assert len(response.json.get("invites")) == 0

        print "#2 ottengo gli inviti, con 1 invito"
        new_game(self, opponent_id)
        response = get_pending_invites(self, opponent_token)
        assert response.json.get("success") == True
        assert len(response.json.get("invites")) == 1

        print "#2 ottengo gli inviti, con 2 inviti"
        new_game(self, opponent_id)
        response = get_pending_invites(self, opponent_token)
        assert response.json.get("success") == True
        assert len(response.json.get("invites")) == 2

        print "#3 ottengo gli inviti, con 3 inviti"
        new_game(self, opponent_id)
        response = get_pending_invites(self, opponent_token)
        assert response.json.get("success") == True
        assert len(response.json.get("invites")) == 3

    def test_get_pending_invites_badge(self):
        #ottengo id e token dell'opponent del quale voglio vedere gli inviti
        opponent_id = self.first_opponent.get("user").get("id")
        opponent_token = self.first_opponent.get("token")

        print "#1 ottengo gli inviti, con 0 inviti"
        response = get_pending_invites_badge(self, opponent_token)
        assert response.json.get("success") == True
        assert response.json.get("badge") == 0

        print "#2 ottengo gli inviti, con 1 invito"
        new_game(self, opponent_id)
        response = get_pending_invites_badge(self, opponent_token)
        assert response.json.get("success") == True
        assert response.json.get("badge") == 1

        print "#2 ottengo gli inviti, con 2 inviti"
        new_game(self, opponent_id)
        response = get_pending_invites_badge(self, opponent_token)
        assert response.json.get("success") == True
        assert response.json.get("badge") == 2

        print "#3 ottengo gli inviti, con 3 inviti"
        new_game(self, opponent_id)
        response = get_pending_invites_badge(self, opponent_token)
        assert response.json.get("success") == True
        assert response.json.get("badge") == 3
