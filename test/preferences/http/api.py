# -*- coding: utf-8 -*-

from tp.preferences.models import Preferences

def changePreferences(self, url, new_value, token = None):
    if not token:
        token = self.token
    return self.app.post(url, token = token, data = {"new_value": new_value})

def getEnumValues(attr):
    return Preferences.__dict__[attr].property.columns[0].type.enums
