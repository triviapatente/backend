# -*- coding: utf-8 -*-

from app import db
from app.preferences.models import *
from app.exceptions import *
from flask import jsonify, g

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
        raise ChangeFailed()
    return jsonify(preferences = preferences)

#ritorna il record di preferenze dell'utente ##user
def getPreferences(user):
    preferences = Preferences.query.filter(Preferences.user_id == user.id).first()
    #non può essere nulla se ha superato auth_required, controllo nel caso per sbaglio venga usato in un altro contesto
    if not preferences:
        raise ChangeFailed()
    return preferences
