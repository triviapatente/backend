# -*- coding: utf-8 -*-
from flask import Blueprint, g, jsonify
from tp.decorators import auth_required, fetch_models, needs_values
from tp.auth.models import User
from tp.game.models import Category
from queries import *
from datetime import datetime, timedelta

stats = Blueprint("stats", __name__, url_prefix = "/stats")

@stats.route("/wrong_answers/<int:category_id>", methods = ["GET"])
@auth_required
@fetch_models(category_id = Category)
def get_wrong_answers(category_id):
    answers = getWrongLastQuestions(category_id)
    return jsonify(answers = answers)

#percentuale riferita a una data
@stats.route("/progresses/<int:category_id>", methods = ["GET"])
@auth_required
@fetch_models(category_id = Category)
def get_progresses(category_id):
    n = 15
    end = datetime.now()
    start = end + timedelta(days=-n)
    progress = getProgressChart(category_id, n, start, end)
    return jsonify(progress = progress)

@stats.route("/categories", methods = ["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify(categories = categories)
