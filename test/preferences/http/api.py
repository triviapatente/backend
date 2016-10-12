# -*- coding: utf-8 -*-

from flask import json
from tp.preferences.models import Preferences

#Utility methods

def changePreferences(self, url, new_value):
    return self.app.post(url, token = self.token, data = {"new_value": new_value})

def getEnumValues(attr):
    return Preferences.__dict__[attr].property.columns[0].type.enums
