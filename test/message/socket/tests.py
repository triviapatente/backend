# -*- coding: utf-8 -*-

from test.shared import TPAuthTestCase, get_socket_client
from test.base.socket.api import join_room
from test.auth.http.api import register
from test.game.http.api import new_game
from api import *

class MessageSocketTestCase(TPAuthTestCase):
    opponent_socket = None
    game_id = None

    def setUp(self):
        super(MessageSocketTestCase, self).setUp(True)
        # creo l'utente con cui conversare
        opponent_id = register(self, "opponent", "opponent@gmail.com", "opponent").json.get("user")["id"]
        # creo un socket per il nuovo utente
        self.opponent_socket = get_socket_client()
        # creo una nuova partita tra l'utente e opponent
        self.game_id = new_game(self, opponent_id).json.get("game")["id"]
        # entrambi gli utenti joinano la loro room
        join_room(self.opponent_socket, self.game_id, "game")
        join_room(self.socket, self.game_id, "game")

    def test_on_message(self):
        content = "Test"

        print "#1: Send message on right room"
        message_sent = send_message(self.game_id, content).json
        # check success
        assert message_sent.get("success")
        # check message and message content
        message = message_sent.get("message")
        assert message and message["content"] == content

        print "#2: Send message on right room, opponent receives message"
        assert False

        print "#3: Send message on wrong room"
        message_sent = send_message(self.game_id + 1, content).json
        # check success == False
        assert message_sent.get("success") == False
