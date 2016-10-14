# -*- coding: utf-8 -*-

from api import *
from test.game.http.api import newGame
from test.auth.http.api import register

class MessageHTTPTestCase(TPAuthTestCase):
    ###TEST METHODS###
    #per creare un metodo di test basta mettere test_ prima del metodo
    def test_list(self):
        #creo un secondo utente ed una partita tra i due
        opponent_id = register(self, "opponent", "opponent@gmail.com", "opponent").get("user")["id"]
        game_id = newGame(self, opponent_id)

        # TODO add messages

        print "#1: Message list received"
        assert getList(self, game_id)
