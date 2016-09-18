# -*- coding: utf-8 -*-
from flask import Blueprint, g
from app.decorators import auth_required, needs_post_values
from app.preferences.utils import *

preferences = Blueprint("preferences", __name__, url_prefix = "/preferences")

# ##notification_type rappresenta l'attributo booleano da invertire
@preferences.route("/notification/<string:notification_type>/edit", methods = ["POST"])
@auth_required
@needs_post_values("new_value")
def changeNotificationPreferences(notification_type):
    #cambio l'attributo richiesto se possibile
    return changePreference("notification_" + notification_type, g.post.get("new_value"))

# ##new_value in questo caso potrebbe essere 'all', o 'friends', o 'nobody'
@preferences.route("/stats/edit", methods = ["POST"])
@auth_required
@needs_post_values("new_value")
def changeStatsPreferences():
    #cambio l'attributo stats se possibile
    return changePreference("stats", g.post.get("new_value"))

# ##new_value in questo caso potrebbe essere 'all', o 'friends', o 'nobody'
@preferences.route("/chat/edit", methods = ["POST"])
@auth_required
@needs_post_values("new_value")
def changeChatPreferences():
    #cambio l'attributo chat se possibile
    return changePreference("chat", g.post.get("new_value"))
