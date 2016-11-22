# -*- coding: utf-8 -*-

from test.shared import TPAuthTestCase
from api import *
from test.game.http.api import new_game, process_invite
from test.auth.http.api import register
from test.auth.socket.api import login
from test.shared import get_socket_client
class BaseSocketTestCase(TPAuthTestCase):
    game = None
    opponent = None
    opponent_id = None
    opponent_token = None
    def setUp(self):
        super(BaseSocketTestCase, self).setUp(socket = True)
        opponent_response = register(self, "opponent", "opponent@gmail.com", "opponent")
        self.opponent = opponent_response.json.get("user")
        self.opponent_id = self.opponent.get("id")
        self.opponent_token = opponent_response.json.get("token")
        # creo un socket per il nuovo utente
        self.opponent_socket = get_socket_client()
        # il socket opponent accede
        login(self, self.opponent_socket, self.opponent_token)
        #viene eseguito prima di ogni singolo metodo
        response = new_game(self, self.opponent.get("id"))
        self.game = response.json.get("game")
        process_invite(self, self.game.get("id"), True, self.opponent_token)
        #per intercettare e rendere 'innocuo' l'evento di accettazione invito
        self.socket.get_received()

    def test_join_room(self):
        game_id = self.game.get("id")

        print "#1: Mi iscrivo a una room a cui posso entrare"
        response = join_room(self.socket, game_id, "game")
        assert response.json.get("success") == True

        print "#2: Mi iscrivo a una room a cui non posso entrare"
        response = join_room(self.socket, 324234, "game")
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3: Mi iscrivo a una room di tipo non conosciuto"
        response = join_room(self.socket, game_id, "adfdsfsfd")
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4: Parametri mancanti"

        print "#4.1: room type"
        response = join_room(self.socket, game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#4.2: room id"
        response = join_room(self.socket, None, "game")
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5: Mi iscrivo a una room in cui son già entrato"
        response = join_room(self.socket, game_id, "game")
        assert response.json.get("success") == True

        print "#6: Event Test: io e l'opponent ci iscriviamo alla stessa room, mi arriva l'evento di join"
        join_room(self.socket, game_id, "game")
        join_room(self.opponent_socket, game_id, "game")
        #ottengo evento
        response = self.socket.get_received()
        assert response.json.get("action") == "joined"
        assert response.json.get("user")
        assert response.json.get("user").get("id") == self.opponent_id

    def test_leave_room(self):
        game_id = self.game.get("id")
        join_room(self.socket, game_id, "game")

        print "#1: Mi tolgo da una room in cui sono presente"
        response = leave_room(self.socket, game_id, "game")
        assert response.json.get("success") == True

        print "#2: Mi tolgo da una room in cui non sono presente"
        response = leave_room(self.socket, game_id, "game")
        assert response.json.get("success") == True

        print "#3: Mi tolgo da una room di tipo non conosciuto"
        response = leave_room(self.socket, game_id, "iojererj")
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4: Parametri mancanti"

        print "#4.1: room type"
        response = leave_room(self.socket, game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#4.2: room id"
        response = leave_room(self.socket, None, "game")
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5: Event Test: l'opponent si disiscrive dalla stessa room, mi arriva l'evento di leave"
        join_room(self.opponent_socket, game_id, "game")
        join_room(self.socket, game_id, "game")
        leave_room(self.opponent_socket, game_id, "game")
        #ottengo evento
        response = self.socket.get_received()
        assert response.json.get("action") == "left"
        assert response.json.get("user")
        assert response.json.get("user").get("id") == self.opponent_id
