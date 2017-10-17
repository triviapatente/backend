# -*- coding: utf-8 -*-
from tp import db
from tp.auth.models import *
from sqlalchemy import func, distinct, desc
from sqlalchemy.orm import aliased
from flask import g
from tp import db

# query che ritorna i primi n utenti in classifica
def getTopRank():
    return User.query.order_by(User.score.desc()).limit(app.config["RESULTS_LIMIT_RANK_ITALY"]).all()

# query che ritorna i primi n utenti in classifica
def getRank():
    #numero di utenti max da ritornare
    limit = app.config["RESULTS_LIMIT_RANK_ITALY"]
    # non sono tra i primi n utenti della classifica
    if getUserPosition(g.user) > limit:
        #in tal caso, ritorno i primi n/2 - 1 utenti maggiori e i primi n/2 minori, assieme a me
        q_min = User.query.order_by(User.score.desc()).filter(User.score >= g.user.score).limit(limit / 2)
        q_max = User.query.order_by(User.score.desc()).filter(User.score < g.user.score).limit(limit / 2)
        query = q_min.union(q_max).alias("rank")
        return db.session.query(query)
    else:
        return getTopRank()

#ottiene la classifica con le informazioni di paginazione
#direction = up/down
#esempio: se ho bisogno degli utenti con punteggio maggiore di n, thresold diventa n, mentre direction diventa up
def getPaginatedRank(thresold, direction):
    a = aliased(User, name = "a")
    position = db.session.query(func.count(distinct(a.score)) + 1).filter(a.score > User.score)
    query = User.query.with_entities(User, position.label("position")).order_by(desc("position"))
    if direction == "up":
        query = query.filter(User.score > thresold)
    else:
        query = query.filter(User.score < thresold)
    return query.all()
#ottiene la posizione dell'utente
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
