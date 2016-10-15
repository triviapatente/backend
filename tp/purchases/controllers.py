# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from tp import app, db
from tp.purchases.models import *

shop = Blueprint("shop", __name__, url_prefix = "/shop")

@shop.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

@shop.route("/list", methods = ["GET"])
def getItems():
    output = ShopItem.query.all()
    print "Anonymous user got shop items list."
    return jsonify(items = output)
