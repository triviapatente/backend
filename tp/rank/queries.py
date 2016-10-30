# -*- coding: utf-8 -*-
from tp import db
from tp.auth.models import *
from sqlalchemy import func, distinct
from tp import db
# ritorna la classifica
def getRank():
    return User.query.order_by(User.score).limit(app.config["RESULTS_LIMIT_RANK_ITALY"]).all()

def getUserPosition(user):
    return db.session.query(func.count(distinct(User.score))).filter(User.score > user.score).scalar() + 1
