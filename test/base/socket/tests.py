# -*- coding: utf-8 -*-

from test.shared import TPAuthTestCase
from api import *
from test.game.http.api import new_game
from test.auth.http.api import register
class BaseSocketTestCase(TPAuthTestCase):
    game = None
    opponent = None
    def setUp(self):
        super(BaseSocketTestCase, self).setUp(True)
        response = register(self, "opponent", "opponent@gmail.com", "opponent")
        self.opponent = response.json.get("user")
        #viene eseguito prima di ogni singolo metodo
        response = new_game(self, self.opponent.get("id"))
        self.game = response.json.get("game")
        print self.game, self.opponent

    def test_join_room(self):
        game_id = self.game.get("id")

        print "#1 mi iscrivo a una room a cui posso entrare"
        response = join_room(self, game_id, "game")
        assert response.json.get("success") == True

        print "#2 mi iscrivo a una room a cui non posso entrare"
        response = join_room(self, 324234, "game")
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#3 mi iscrivo a una room di tipo non conosciuto"
        response = join_room(self, game_id, "adfdsfsfd")
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4 Parametri mancanti"

        print "#4.1 Manca room type"
        response = join_room(self, game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#4.2 Manca room id"
        response = join_room(self, None, "game")
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#5 mi iscrivo a una room in cui son già entrato"
        response = join_room(self, game_id, "game")
        assert response.json.get("success") == True

    def test_leave_room(self):
        game_id = self.game.get("id")

        print "#1 mi tolgo da una room in cui sono presente"
        join_room(self, game_id, "game")
        response = leave_room(self, game_id, "game")
        assert response.json.get("success") == True

        print "#2 mi tolgo da una room in cui non sono presente"
        response = leave_room(self, game_id, "game")
        assert response.json.get("success") == True

        print "#3 mi tolgo da una room di tipo non conosciuto"
        response = leave_room(self, game_id, "iojererj")
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#4 Parametri mancanti"

        print "#4.1 Manca room type"
        response = leave_room(self, game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#4.2 Manca room id"
        response = leave_room(self, None, "game")
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400
