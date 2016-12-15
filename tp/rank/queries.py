# -*- coding: utf-8 -*-
from tp import db
from tp.auth.models import *
from sqlalchemy import func, distinct, desc
from sqlalchemy.orm import aliased
from tp import db
# ritorna la classifica
def getRank():
    return User.query.order_by(User.score.desc()).limit(app.config["RESULTS_LIMIT_RANK_ITALY"]).all()

def getUserPosition(user):
    return db.session.query(func.count(distinct(User.score))).filter(User.score > user.score).scalar() + 1

def search(query):
    #SELECT *,
        #(SELECT COUNT(DISTINCT score) + 1
        #FROM public.user
        #WHERE score > a.score) as position
    #FROM public.user a
    #WHERE username LIKE '%query%'
    a = aliased(User, name = "a")
    position = db.session.query(func.count(distinct(a.score)) + 1).filter(a.score > User.score)
    output = User.query.with_entities(User, position.label("position")).filter(User.username.ilike(query)).order_by(desc("position")).all()
    matches = []
    for item in output:
        match = item[0]
        match.position = item[1]
        matches.append(match)
    return matches
