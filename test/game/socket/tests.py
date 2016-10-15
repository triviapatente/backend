# -*- coding: utf-8 -*-

from test.auth.http.api import register
from test.auth.socket.api import login
from test.game.http.api import new_game
from test.shared import get_socket_client, TPAuthTestCase
from test.base.socket.api import join_room, leave_room
from api import *
from tp.game.models import Round
from tp import db
from sqlalchemy.exc import IntegrityError
class GameSocketTestCase(TPAuthTestCase):

    opponent_id = None
    opponent_token = None
    opponent_socket = None
    game_id = None
    game = None
    def setUp(self):
        super(GameSocketTestCase, self).setUp(socket = True)
        response = register(self, "opponent", "opponent@gmail.com", "opponent")
        self.opponent_id = response.json.get("user").get("id")
        self.opponent_token = response.json.get("token")
        self.opponent_socket = get_socket_client()
        login(self, self.opponent_socket, self.opponent_token)
        self.game = new_game(self, self.opponent_id).json.get("game")
        self.game_id = self.game.get("id")
        join_room(self.socket, self.game_id, "game")
        join_room(self.opponent_socket, self.game_id, "game")

    def test_init_round(self):
        print "#1 creo due round con number uguale e game uguale"
        r = Round(game_id = self.game_id, number = 1, dealer_id = self.opponent_id)
        db.session.add(r)
        r = Round(game_id = self.game_id, number = 1, dealer_id = self.opponent_id)
        db.session.add(r)
        try:
            db.session.commit()
            assert False, "Duplicate key-value not called"
        except IntegrityError:
            pass

        print "#2 Creo un round senza essere iscritto alla room"
        leave_room(self.socket, self.game_id, "game")
        response = init_round(self.socket, self.game_id, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403
        join_room(self.socket, self.game_id, "game")

        print "#3 Creo il primo round e il dealer è il creatore della partita"
        Round.query.delete()
        response = init_round(self.opponent_socket, self.game_id, 1)
        assert response.json.get("success") == True
        assert response.json.get("round")
        assert response.json.get("round").get("dealer_id") == self.game.get("creator_id")

        print "#4 Accedo al round ma il dealer ne sta scegliendo la categoria"
        Round.query.delete()
        init_round(self.socket, self.game_id, 1)
        response = init_round(self.opponent_socket, self.game_id, 1)
        assert response.json.get("success") == True
        assert response.json.get("round")
        assert response.json.get("waiting") == "category"

        print "#5 Accedo al round ma colui che dovrebbe essere il nuovo dealer sta ancora giocando il precedente"



        print "#6 Accedo a un round senza aver risposto alle domande del precedente"
        Round.query.delete()
        response = init_round(self.socket, self.game_id, 1)
        response = init_round(self.socket, self.game_id, 2)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 403

        print "#7 Creo un round che non è il primo e ricevo le precedenti risposte"

        print "#8 Parametri mancanti"
        print "#8.1 game_id"
        Round.query.delete()
        response = init_round(self.socket, None, 1)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

        print "#8.2 number"
        Round.query.delete()
        response = init_round(self.socket, self.game_id, None)
        assert response.json.get("success") == False
        assert response.json.get("status_code") == 400

    def test_get_categories(self):
        pass
    def test_choose_category(self):
        pass
    def test_get_questions(self):
        pass
    def test_answer(self):
        pass
