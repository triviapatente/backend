# -*- coding: utf-8 -*-

from tp.preferences.models import Preferences
from test.shared import TPAuthTestCase
from test.preferences.http.api import *

class PreferencesHTTPTestCase(TPAuthTestCase):
    def test_changeNotificationPreferences(self):
        # prendo tutte gli attributi con il ##notification_prefix
        notification_prefix = "notification_"
        notification_types = [notification_type[len(notification_prefix):] for notification_type in Preferences.__dict__.keys() if notification_prefix in notification_type]
        for i in range(0, len(notification_types)):
            print(f"#{i+1}: Cambio notifiche {notification_types[i]} effettuato")
            # essendo di default True, testo che diventi False
            response = changePreferences(self, f"/preferences/notification/{notification_types[i]}/edit", False)
            assert response.status_code == 200 and response.json.get("preferences").get(notification_prefix + notification_types[i]) == False

    def test_changeStatsPreferences(self):
        url = "/preferences/stats/edit"
        # prendo i possibili valori di stats
        enum_values = getEnumValues("stats")
        for i in range(0, len(enum_values)):
            # provo a settare ciascun valore per stats
            print(f"#{i+1}: Cambio preferenze statistiche in {enum_values[i]}")
            response = changePreferences(self, url, enum_values[i])
            assert response.status_code == 200 and response.json.get("preferences").get("stats") == enum_values[i]

    def test_changeChatPreferences(self):
        url = "/preferences/chat/edit"
        # prendo i possibili valori di chat
        enum_values = getEnumValues("chat")
        for i in range(0, len(enum_values)):
            # provo a settare ciascun valore per chat
            print(f"#{i+1}: Cambio preferenze chat in {enum_values[i]}")
            response = changePreferences(self, url, enum_values[i])
            assert response.status_code == 200 and response.json.get("preferences").get("chat") == enum_values[i]
