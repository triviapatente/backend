# -*- coding: utf-8 -*-

from test.shared import TPAuthTestCase
from tp.preferences.models import Preferences
from api import *

class PreferencesHTTPTestCase(TPAuthTestCase):
    def test_changeNotificationPreferences(self):
        # prendo tutte gli attributi con il ##notification_prefix
        notification_prefix = "notification_"
        notification_types = [notification_type[len(notification_prefix):] for notification_type in Preferences.__dict__.keys() if notification_prefix in notification_type]
        for i in range(0, len(notification_types)):
            print "#" + str(i+1) + ": Cambio notifiche %s effettuato" % notification_types[i]
            # essendo di default True, testo che diventi False
            response = changePreferences(self, "/preferences/notification/%s/edit" % notification_types[i], False)
            assert response.status_code == 200 and response.json.get("preferences").get(notification_prefix + notification_types[i]) == False

    def test_changeStatsPreferences(self):
        url = "/preferences/stats/edit"
        # prendo i possibili valori di stats
        enum_values = getEnumValues("stats")
        for i in range(0, len(enum_values)):
            # provo a settare ciascun valore per stats
            print "#" + str(i+1) + ": Cambio preferenze statistiche in %s" % enum_values[i]
            response = changePreferences(self, url, enum_values[i])
            assert response.status_code == 200 and response.json.get("preferences").get("stats") == enum_values[i]

    def test_changeChatPreferences(self):
        url = "/preferences/chat/edit"
        # prendo i possibili valori di chat
        enum_values = getEnumValues("chat")
        for i in range(0, len(enum_values)):
            # provo a settare ciascun valore per chat
            print "#" + str(i+1) + ": Cambio preferenze chat in %s" % enum_values[i]
            response = changePreferences(self, url, enum_values[i])
            assert response.status_code == 200 and response.json.get("preferences").get("chat") == enum_values[i]
