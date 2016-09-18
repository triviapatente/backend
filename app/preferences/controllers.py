# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint, g
from app import app, db
from app.auth.models import *
from app.decorators import auth_required, needs_post_values
from app.exceptions import *

preferences = Blueprint("preferences", __name__, url_prefix = "/preferences")

@preferences.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

@preferences.route("/notification/<string:notification_type>", methods = ["POST"])
@auth_required
def changeNotificationPreferences(notification_type):
    #prendo le preferenze dell'utente
    preferences = Preferences.query.filter(Preferences.user_id == g.user.id).first()
    #non può essere nulla se ha superato auth_required, in ogni caso controlliamo
    if not preferences:
        raise ChangeFailed()
    #costruisco l'attributo da modificare
    notification_type = "notification_" + notification_type
    #provo a modificare la preferenza richiesta
    try:
        #nego la precedente proprietà
        setattr(preferences, notification_type, not getattr(preferences, notification_type))
    except:
        #se ad esempio la proprietà non esiste o non si può modificare per qualche altro motivo da errore
        raise ChangeFailed()
    db.session.add(preferences)
    db.session.commit()
    return jsonify(preferences)
