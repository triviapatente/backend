# -*- coding: utf-8 -*-
from flask import Blueprint, g, jsonify
from tp.decorators import auth_required, fetch_models, needs_values
from tp.auth.models import User
from tp.game.models import Category
from queries import *
from datetime import datetime, timedelta

stats = Blueprint("stats", __name__, url_prefix = "/stats")

@stats.route("/detail/<int:category_id>", methods = ["GET"])
@auth_required
@fetch_models(category_id = Category)
def get_info(category_id):
    n = 15
    end = datetime.now()
    start = end + timedelta(days = -n)
    progress = getProgressChart(category_id, n, start, end)
    wrong_answers = getWrongLastQuestions(category_id)
    return jsonify(success = True, progress = progress, wrong_answers = wrong_answers)

@stats.route("/categories", methods = ["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify(success = True, categories = categories)
