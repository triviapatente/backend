# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from app import app, db
from app.auth.models import *

preferences = Blueprint("preferences", __name__, "/preferences")

@preferences.route("/", methods = ["GET"])
def welcome:
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)
