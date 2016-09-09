# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from app import app, db
from app.push.models import *

push = Blueprint("push", __name__, url_prefix = "/push")

@push.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)
