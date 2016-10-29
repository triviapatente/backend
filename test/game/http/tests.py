# -*- coding: utf-8 -*-

from api import *
from test.shared import TPAuthTestCase, get_socket_client
from tp.game.models import Invite, Game, Partecipation
from test.auth.http.api import register
from test.auth.socket.api import login
from test.base.socket.api import leave_room, join_room

from tp import db
class GameHTTPTestCase(TPAuthTestCase):
    first_opponent = None
    second_opponent = None
    third_opponent = None

    first_opponent_socket = None
    def setUp(self):
        super(GameHTTPTestCase, self).setUp(socket = True)
        self.first_opponent = register(self, "test1", "test1@gmail.com", "test").json
        self.first_opponent_socket = get_socket_client()
        login(self, self.first_opponent_socket, self.first_opponent.get("token"))
        self.second_opponent = register(self, "test2", "test2@gmail.com", "test").json
        self.third_opponent = register(self, "test3", "test3@gmail.com", "test").json

    def test_new_game(self):
        opponent_id = self.first_opponent.get("user").get("id")

        print "#1: Creazione game"
        response = new_game(self, opponent_id)
        assert response.json.get("success") == True
        assert response.json.get("game")
        assert response.json.get("user")

        print "#2 Event Test: l'avversario ha ricevuto l'evento"
        response = self.first_opponent_socket.get_received()
        assert response.json.get("action") == "create"
        assert response.json.get("game")

        print "#3: Creazione game con utente inesistente"
        response = new_game(self, 32)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#4: Parametri mancanti: utente"
        response = new_game(self, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

    def test_leave_game(self):
        opponent_id = self.first_opponent.get("user").get("id")
        other_opponent_token = self.second_opponent.get("token")

        game_id = new_game(self, opponent_id).json.get("game").get("id")
        #per intercettare e rendere 'innocuo' l'evento di creazione del game
        self.first_opponent_socket.get_received()

        print "#1: Il game non esiste"
        response = leave_game(self, 200)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#2: Non appartengo alla game"
        other_game_id = new_game(self, opponent_id, token = other_opponent_token).json.get("game").get("id")
        #per intercettare e rendere 'innocuo' l'evento di creazione del game
        self.first_opponent_socket.get_received()

        response = leave_game(self, other_game_id)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3: Parametri mancanti"
        print "#3: game_id"
        response = leave_game(self, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#4: Mi tolgo dal gioco correttamente"
        response = leave_game(self, game_id)
        assert response.json.get("success") == True
        assert response.json.get("partecipations")
        assert response.json.get("game")
        assert response.json.get("ended") == True
        assert response.json.get("winner")

        print "#5 Event Test: l'avversario ha ricevuto l'evento"
        response = self.first_opponent_socket.get_received()
        assert response.json.get("action") == "game_left"
        assert response.json.get("partecipations")
        assert response.json.get("game")
        assert response.json.get("winner")

    def test_random_search(self):

        print "#1: Creazione game"
        response = new_random_game(self)
        assert response.json.get("success") == True
        assert response.json.get("game")
        user1 = response.json.get("user")
        assert user1

        #azzero i database se no l'utente scelto è sempre lo stesso (l'unico con game attivi)
        Partecipation.query.delete()
        db.session.commit()

        print "#2: Creazione game"
        response = new_random_game(self)
        assert response.json.get("success") == True
        assert response.json.get("game")
        user2 = response.json.get("user")
        assert user2

        #azzero i database se no l'utente scelto è sempre lo stesso (l'unico con game attivi)
        Partecipation.query.delete()
        db.session.commit()

        print "#3: Creazione game"
        response = new_random_game(self)
        assert response.json.get("success") == True
        assert response.json.get("game")
        user3 = response.json.get("user")
        assert user3

        print "Opponents: ", user1.get("username"), user2.get("username"), user3.get("username")

    def test_get_pending_invites(self):
        #ottengo id e token dell'opponent del quale voglio vedere gli inviti
        opponent_id = self.first_opponent.get("user").get("id")
        opponent_token = self.first_opponent.get("token")

        print "#1: Ottengo gli inviti, con 0 inviti"
        response = get_pending_invites(self, opponent_token)
        assert response.json.get("success") == True
        assert len(response.json.get("invites")) == 0

        print "#2: Ottengo gli inviti, con 1 invito"
        new_game(self, opponent_id)
        response = get_pending_invites(self, opponent_token)
        assert response.json.get("success") == True
        assert len(response.json.get("invites")) == 1

        print "#3: Ottengo gli inviti, con 2 inviti"
        new_game(self, opponent_id)
        response = get_pending_invites(self, opponent_token)
        assert response.json.get("success") == True
        assert len(response.json.get("invites")) == 2

        print "#4: Ottengo gli inviti, con 3 inviti"
        new_game(self, opponent_id)
        response = get_pending_invites(self, opponent_token)
        assert response.json.get("success") == True
        assert len(response.json.get("invites")) == 3

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

        print "#1: accetto un invito di un game valido"
        #Accetto
        response = process_invite(self, game_id, True, opponent_token)
        assert response.json.get("success") == True
        assert response.json.get("invite")

        print "#2: accetto/ rifiuto un invito già accettato (o rifiutato eventualmente)"
        response = process_invite(self, game_id, False, opponent_token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3: accetto/rifiuto un invito di un game inesistente"
        #Accetto
        response = process_invite(self, 32423, True, opponent_token, )
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#4: accetto/rifiuto un invito di un game a cui non partecipo"
        #Accetto
        response = process_invite(self, foreign_game.get("id"), True, opponent_token)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#5: Parametri mancanti"
        print "#5.1: accept"
        response = process_invite(self, game_id, None, opponent_token)
        assert response.json.get("success") == False
        print response.json.get("status_code")
        assert response.json.get("status_code") == 400
