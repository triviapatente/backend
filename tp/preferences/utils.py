# -*- coding: utf-8 -*-

from tp import db
from tp.preferences.models import *
from tp.exceptions import *
from flask import jsonify, g
from tp.preferences.queries import *

#metodo per cambiare una preferenza
# ##user è l'utente, ##attribute_to_change è l'attributo da cambiare, ##new_value è il nuovo valore
def changePreference(attribute_to_change, new_value):
    preferences = getPreferences(g.user)
    #provo a modificare la preferenza richiesta
    preferences[attribute_to_change] = new_value
    try:
        db.session.add(preferences)
        db.session.commit()
    except:
        #se la proprietà non esiste o non è ammesso il nuovo valore o non si può modificare per qualche motivo do errore
        print(f"User {g.user.username} attempt to modify {attribute_to_change} without success.")
        raise ChangeFailed()
    print(f"User {g.user.username} success in modify {attribute_to_change}.")
    return jsonify(preferences = preferences)

#ritorna il record di preferenze dell'utente ##user
def getPreferences(user):
    preferences = getPreferencesFromUserID(user.id)
    #non può essere nulla se ha superato auth_required, controllo nel caso per sbaglio venga usato in un altro contesto
    if not preferences:
        raise ChangeFailed()
    return preferences
