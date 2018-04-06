# -*- coding: utf-8 -*-
from flask import Blueprint, g, jsonify
from tp.decorators import auth_required, fetch_models, needs_values
from tp.auth.models import User
from tp.game.models import Category
from queries import *
from datetime import datetime, timedelta

stats = Blueprint("stats", __name__, url_prefix = "/stats")

@stats.route("/detail/", methods = ["GET"])
@auth_required
def obtain_general_infos():
    output = getCategoryInfo(None)
    return jsonify(output)

@stats.route("/detail/<int:category_id>", methods = ["GET"])
@auth_required
@fetch_models(category_id = Category)
def obtain_category_infos(category_id):
    output = getCategoryInfo(category_id)
    return jsonify(output)

@stats.route("/categories", methods = ["GET"])
def obtain_categories():
    categories = Category.query.all()
    return jsonify(success = True, categories = categories)
