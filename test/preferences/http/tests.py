# -*- coding: utf-8 -*-

from test.shared import TPTestCase
from flask import json
from app.preferences.models import Preferences
class PreferencesHTTPTestCase(TPTestCase):
    #Utility methods

    # mi tocca copiarli per via delle circular references
    # TODO find a better way to do it
    def login(self, username, password):
        response = self.app.post("/auth/login", data = {"user": username, "password": password})
        response.json = json.loads(response.data)
        return response
    def register(self, username, email, password):
        response = self.app.post("/auth/register", data = {"username": username, "email": email, "password": password})
        response.data = response.data.encode("utf-8")
        response.json = json.loads(response.data)
        return response

    def changePreferences(self, url, token, new_value):
        response = self.app.post(url, headers = {"tp-session-token":token}, data = {"new_value": new_value})
        response.json = json.loads(response.data)
        return response

    def getEnumValues(self, attr):
        return Preferences.__dict__[attr].property.columns[0].type.enums

    ###TEST METHODS###
    #per creare un metodo di test basta mettere test_ prima del metodo

    def test_changeNotificationPreferences(self):
        self.register("user", "user@gmail.com", "user")
        token = self.login("user", "user").json.get("token")

        # prendo tutte gli attributi con il ##notification_prefix
        notification_prefix = "notification_"
        notification_types = [notification_type[len(notification_prefix):] for notification_type in Preferences.__dict__.keys() if notification_prefix in notification_type]

        for i in range(0, len(notification_types)):
            print "#" + str(i+1) + ": Cambio notifiche %s effettuato" % notification_types[i]
            # essendo di default True, testo che diventi False
            response = self.changePreferences("/preferences/notification/%s/edit" % notification_types[i], token, False)
            assert response.status_code == 200 and response.json.get("preferences").get(notification_prefix + notification_types[i]) == False

    def test_changeStatsPreferences(self):
        url = "/preferences/stats/edit"
        self.register("user", "user@gmail.com", "user")
        token = self.login("user", "user").json.get("token")

        enum_values = self.getEnumValues("stats")
        for i in range(0, len(enum_values)):
            print "#" + str(i+1) + ": Cambio preferenze statistiche in %s" % enum_values[i]
            response = self.changePreferences(url, token, enum_values[i])
            assert response.status_code == 200 and response.json.get("preferences").get("stats") == enum_values[i]


    def test_changeChatPreferences(self):
        url = "/preferences/chat/edit"
        self.register("user", "user@gmail.com", "user")
        token = self.login("user", "user").json.get("token")

        enum_values = self.getEnumValues("chat")
        for i in range(0, len(enum_values)):
            print "#" + str(i+1) + ": Cambio preferenze chat in %s" % enum_values[i]
            response = self.changePreferences(url, token, enum_values[i])
            assert response.status_code == 200 and response.json.get("preferences").get("chat") == enum_values[i]
