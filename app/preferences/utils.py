# -*- coding: utf-8 -*-

from app import db
from app.auth.models import *
from app.exceptions import *
from flask import jsonify

#metodo per cambiare una preferenza booleana
# ##user è l'utente, ##attribute_to_switch è l'attributo booleano da invertire
def changeUISwitchPreferences(user, attribute_to_switch):
    preferences = getPreferences(user)
    #provo a modificare la preferenza richiesta
    try:
        #nego la precedente proprietà
        setattr(preferences, attribute_to_switch, not getattr(preferences, attribute_to_switch))
        db.session.add(preferences)
        db.session.commit()
        return jsonify(preferences = preferences)
    except:
        #se ad esempio la proprietà non esiste o non si può modificare per qualche altro motivo do errore
        raise ChangeFailed()

#metodo per cambiare una preferenza tramite choicepicker
# ##user è l'utente, ##attribute_to_change è l'attributo da cambiare, ##choice è il nuovo valore
def changeChoicePickerPreferences(user, attribute_to_change, choice):
    preferences = getPreferences(user)
    #provo a modificare la preferenza richiesta
    try:
        setattr(preferences, attribute_to_change, choice)
        db.session.add(preferences)
        db.session.commit()
        return jsonify(preferences)
    except:
        #se la proprietà non esiste o non è ammesso il nuovo valore o non si può modificare per qualche motivo do errore
        raise ChangeFailed()

#ritorna il record di preferenze dell'utente ##user
def getPreferences(user):
    preferences = Preferences.query.filter(Preferences.user_id == user.id).first()
    #non può essere nulla se ha superato auth_required, controllo nel caso per sbaglio venga usato in un altro contesto
    if not preferences:
        raise ChangeFailed()
    return preferences
