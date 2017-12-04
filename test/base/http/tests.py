# -*- coding: utf-8 -*-

from test.shared import TPAuthTestCase
from api import *

class BaseHTTPTestCase(TPAuthTestCase):
    def test_contact(self):
        print "1. Mando 3 segnalazione corrette, specificando i 3 tipi (tutte di tipo diverso)"
        first = contact(self, "Messaggio di prova", "complaint")
        assert first.json.get("success") == True
        second = contact(self, "Messaggio di prova", "hint")
        assert second.json.get("success") == True
        third = contact(self, "Messaggio di prova", "other")
        assert third.json.get("success") == True

        print "2. Sbaglio il tipo di segnalazione"
        message = contact(self, "Messaggio di prova", "fuffa")
        assert message.json.get("success") == False
        assert message.json.get("status_code") == 400



        print "3.1 Parametri mancanti: message"
        message = contact(self, None, "fuffa")
        assert message.json.get("success") == False
        assert message.json.get("status_code") == 400

        print "3.2 Parametri mancanti: scope"
        message = contact(self, "Messaggio di prova", None)
        assert message.json.get("success") == False
        assert message.json.get("status_code") == 400

        print "4. Autenticazione richiesta"
        self.token = "fuffa"
        message = contact(self, "Messaggio di prova", "hint")
        assert message.json.get("success") == False
        assert message.json.get("status_code") == 401
