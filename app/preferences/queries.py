# -*- coding: utf-8 -*-

from app.preferences.models import *

# get preferences of choosen user (from id: ##id)
def getPreferencesFromUserID(id):
    return Preferences.query.filter(Preferences.user_id == id).first()
