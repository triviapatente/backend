# -*- coding: utf-8 -*-

from api import *
from test.auth.http.api import register
from test.game.http.api import new_game, process_invite
from test.base.socket.api import join_room
from test.message.socket.api import send_message
from tp import app
from test.shared import TPAuthTestCase, get_socket_client
from datetime import datetime

class MessageHTTPTestCase(TPAuthTestCase):
    opponent_socket = None
    game_id = None
    messages = []
    maxMessages = app.config["MESSAGE_PER_SCROLL"]

    def setUp(self):
        super(MessageHTTPTestCase, self).setUp(True)
        # creo l'utente con cui conversare
        opponent_response = register(self, "opponent", "opponent@gmail.com", "opponent").json
        opponent_id = opponent_response.get("user").get("id")
        opponent_token = opponent_response.get("token")
        # creo un socket per il nuovo utente
        self.opponent_socket = get_socket_client()
        # creo una nuova partita tra l'utente e opponent
        self.game_id = new_game(self, opponent_id).json.get("game")["id"]
        process_invite(self, self.game_id, True, opponent_token)
        #per intercettare e rendere 'innocuo' l'evento di accettazione invito
        self.socket.get_received()
        # entrambi gli utenti joinano la loro room
        join_room(self.opponent_socket, self.game_id, "game")
        join_room(self.socket, self.game_id, "game")
        # creo un numero di messaggi superiore a quello di massimo di getList
        for i in range(0, self.maxMessages + 10):
            self.messages.append(send_message(self.socket, self.game_id, "Message%s" % i).json.get("message"))

    ###TEST METHODS###
    #per creare un metodo di test basta mettere test_ prima del metodo
    def test_list(self):
        # prendo la data dell'11esimo messaggio
        datetime = self.messages[10]["updatedAt"]

        print "#1: Message list from %s received" % datetime
        # prendo i primi 10 messaggi (i primi 50 più vecchi dopo l'11esimo sono i primi 10)
        messageList = getList(self, self.game_id, datetime).json.get("messages")
        # controllo di avere messaggi
        assert messageList

        print "#2: Number of messages less then max per scroll when there are less then max to get"
        # controllo che il numero di messaggi sia minore del massimo per scroll quando il numero di messaggi più vecchi della data son meno del massimo
        assert len(messageList) <= self.maxMessages

        print "#3: Check messages content"
        # controllo che il contenuto dei messaggi tornati sia quello dei 10 più vecchi
        for i in range(0, 10):
            assert self.messages[i]["content"] == messageList[i]["content"]

        print "#4: Number of messages less then max per scroll when there are more then max to get"
        # come 2 ma ce ne sono più del massimo che sono più vecchi di quella data
        messageList = getList(self, self.game_id).json.get("messages")
        assert len(messageList) <= self.maxMessages
