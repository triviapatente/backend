from api import *
from test.shared import TPAuthTestCase
from tp.game.models import Invite, Game
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

    def test_process_invite(self):
        #ottengo id e token dell'opponent del quale voglio vedere gli inviti
        opponent_id = self.first_opponent.get("user").get("id")
        opponent_token = self.first_opponent.get("token")
        #game in cui partecipo
        game_id = new_game(self, opponent_id).json.get("game").get("id")
        #ottengo l'id di un altro utente
        other_opponent_id = self.second_opponent.get("user").get("id")
        #game in cui NON partecipo (ho passato il token di un altro utente come terzo parametro, e quindi la chiamata viene fatta come se fossi quell'utente)
        foreign_game = new_game(self, other_opponent_id, opponent_token).json.get("game")

        print "#1 accetto/rifiuto un invito di un game valido"
        response = process_invite(self, game_id, True, opponent_token)
        assert response.json.get("success") == True
        assert response.json.get("invite")

        response = process_invite(self, game_id, False, opponent_token)
        assert response.json.get("success") == True
        assert response.json.get("invite")

        print "#2 accetto/rifiuto un invito di un game inesistente"
        response = process_invite(self, 32423, True, opponent_token, )
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        response = process_invite(self, 32423, False, opponent_token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#3 accetto/rifiuto un invito di un game a cui non partecipo"
        response = process_invite(self, foreign_game.get("id"), True, opponent_token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        response = process_invite(self, foreign_game.get("id"), False, opponent_token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4 Parametri mancanti"
        print "#4.1 accept mancante"
        response = process_invite(self, game_id, None, opponent_token)
        assert response.json.get("success") == False
        print response.json.get("status_code")
        assert response.json.get("status_code") == 400
