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
    #costruisco l'attributo da modificare
    notification_type = "notification_" + notification_type
    #cambio l'attributo costruto, se esiste
    return changeUISwitchPreferences(g.user, notification_type)

# ##new_value in questo caso potrebbe essere 'all', o 'friends', o 'nobody'
@preferences.route("/stats/edit", methods = ["POST"])
@auth_required
@needs_post_values("new_value")
def changeStatsPreferences(new_value):
    #cambio l'attributo stats se possibile
    return changeChoicePickerPreferences(g.user, "stats", new_value)

# ##new_value in questo caso potrebbe essere 'all', o 'friends', o 'nobody'
@preferences.route("/chat/edit", methods = ["POST"])
@auth_required
@needs_post_values("new_value")
def changeChatPreferences(new_value):
    #cambio l'attributo chat se possibile
    return changeChoicePickerPreferences(g.user, "chat", new_value)
