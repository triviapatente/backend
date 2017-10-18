# -*- coding: utf-8 -*-
from tp import db
from tp.auth.models import *
from sqlalchemy import func, distinct, desc, asc
from sqlalchemy.orm import aliased
from flask import g
from tp import db

# query che ritorna i primi n utenti in classifica
def getTopRank():
    limit = app.config["RESULTS_LIMIT_RANK_ITALY"]
    entities = userAndPositionEntities()
    return User.query.with_entities(*entities).order_by(asc("position")).limit(limit).all()

#tutte le colonne di user, più position
def userAndPositionEntities():
    columns = [c for c in User.__table__.c]
    position = getPositionJoin().label("position")
    columns.append(position)
    return columns

# query che ritorna i primi n utenti in classifica
def getRank():
    #numero di utenti max da ritornare
    limit = app.config["RESULTS_LIMIT_RANK_ITALY"]
    # non sono tra i primi n utenti della classifica
    if getUserPosition(g.user) > limit:
        entities = userAndPositionEntities()
        #in tal caso, ritorno i primi n/2 - 1 utenti maggiori e i primi n/2 minori, assieme a me
        q_min = User.query.with_entities(*entities).order_by(desc("position")).filter(User.score >= g.user.score).limit(limit / 2).all()
        q_min.reverse()
        q_max = User.query.with_entities(*entities).order_by(asc("position")).filter(User.score < g.user.score).limit(limit / 2).all()
        return q_min + q_max
    else:
        return getTopRank()

#ottiene la classifica con le informazioni di paginazione
#direction = up/down
#esempio: se ho bisogno degli utenti con punteggio maggiore di n, thresold diventa n, mentre direction diventa up
def getPaginatedRank(thresold, direction):
    entities = userAndPositionEntities()
    limit = app.config["RESULTS_LIMIT_RANK_ITALY"]
    query = User.query.with_entities(*entities)
    if direction == "up":
        output = query.filter(User.score > thresold).order_by(desc("position")).limit(limit).all()
        output.reverse()
        return output
    else:
        return query.filter(User.score < thresold).order_by(asc("position")).limit(limit).all()

def getPositionJoin():
    a = aliased(User, name = "a")
    return db.session.query(func.count(distinct(a.score)) + 1).filter(a.score > User.score)

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
    entities = userAndPositionEntities()
    return User.query.with_entities(*entities).filter(User.username.ilike(query)).order_by(asc("position")).all()
