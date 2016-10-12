# -*- coding: utf-8 -*-

from flask import json
from tp.preferences.models import Preferences

#Utility methods

def changePreferences(self, url, new_value):
    response = self.app.post(url, headers = {"tp-session-token":self.token}, data = {"new_value": new_value})
    response.json = json.loads(response.data)
    return response

def getEnumValues(attr):
    return Preferences.__dict__[attr].property.columns[0].type.enums
