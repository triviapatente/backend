# -*- coding: utf-8 -*-
from tp import db
from tp.auth.models import *
from tp.game.models import Partecipation, Game

from sqlalchemy import func, distinct, desc, asc, or_, and_
from sqlalchemy.orm import aliased
from flask import g
from tp import db
from utils import *

# query che ritorna i primi n utenti in classifica
def getTopRank(exclude_me = False):
    limit = app.config["RESULTS_LIMIT_RANK_ITALY"]
    alias = aliased(User, name = "a")
    (internalPosition, position, lastGameResult) = (getInternalPositionJoin(alias), getPositionJoin(alias), getLastGameResultJoin(alias))
    query = User.query.with_entities(alias, position, internalPosition, lastGameResult)
    if exclude_me:
        query = query.filter(alias.id != g.user.id)
    output = query.order_by(asc("internal_position")).limit(limit).all()
    return sanitizeRankResponse(output)

#tutte le colonne di user, più position
def sanitizeRankResponse(rank):
    output = []
    for user in rank:
        item = user[0]
        item.position = user[1]
        if len(user) > 2:
            item.internalPosition = user[2]
        if len(user) > 3:
            if user[3] is not None:
                item.last_game_won = (user[3] == g.user.id)
        output.append(item)
    return output

#query che ottiene la classifica attorno al mio utente, e non la top_rank
def getLocalRank(exclude_me = False):
    limit = app.config["RESULTS_LIMIT_RANK_ITALY"]
    myUser = g.user
    myUser.position = getUserPosition(myUser)
    myUser.internalPosition = getUserInternalPosition(myUser)

    left_users = getPaginatedRank(myUser.internalPosition, "down", limit / 2)
    right_limit = limit / 2
    if not exclude_me:
        right_limit -= 1
    right_users = getPaginatedRank(myUser.internalPosition, "up", right_limit)
    if not exclude_me:
        left_users.append(myUser)
    return extractArrayFrom(left_users, right_users, limit)

# query che ritorna i primi n utenti in classifica
def getRank(exclude_me = False):
    #numero di utenti max da ritornare
    limit = app.config["RESULTS_LIMIT_RANK_ITALY"]
    # non sono tra i primi n utenti della classifica
    if getUserInternalPosition(g.user) > limit:
        #in tal caso, ritorno i primi n/2 - 1 utenti maggiori e i primi n/2 minori, assieme a me
        return getLocalRank(exclude_me)
    else:
        return getTopRank(exclude_me)

#ottiene la classifica con le informazioni di paginazione
#direction = up/down
#esempio: se ho bisogno degli utenti con internalPosition maggiore di n, thresold diventa n, mentre direction diventa up
def getPaginatedRank(thresold, direction, limit = app.config["RESULTS_LIMIT_RANK_ITALY"]):
    alias = aliased(User, name = "a")
    (position, internalPosition, lastGameResult) = (getPositionJoin(alias), getInternalPositionJoin(alias), getLastGameResultJoin(alias))
    query = User.query.with_entities(alias, position, internalPosition, lastGameResult)
    output = None
    if direction == "up":
        output = query.filter(internalPosition > thresold).order_by(asc("internal_position")).limit(limit).all()
    else:
        output = query.filter(internalPosition < thresold).order_by(desc("internal_position")).limit(limit).all()
        output.reverse()
    return sanitizeRankResponse(output)

def search(query):
    #SELECT *,
        #(SELECT COUNT(DISTINCT score) + 1
        #FROM public.user
        #WHERE score > a.score) as position
    #FROM public.user a
    #WHERE username LIKE '%query%'
    position = getPositionJoin(User)
    output = User.query.with_entities(User, position).filter(User.username.ilike(query)).all()
    return sanitizeRankResponse(output)



#ottiene la posizione dell'utente
def getUserPosition(user):
    query = userPositionQuery(User, user)
    print query
    return query.scalar()
#ottiene la posizione interna dell'utente
def getUserInternalPosition(user):
    query = userInternalPositionQuery(User, user)
    print query
    return query.scalar()


def getLastGameResultJoin(user):
    user_games = Partecipation.query.with_entities(Partecipation.game_id).filter(Partecipation.user_id == g.user.id)
    return Partecipation.query.filter(Partecipation.user_id == user.id).filter(Partecipation.game_id.in_(user_games)).join(Game).with_entities(Game.winner_id).filter(Game.ended == True).order_by(Game.createdAt.desc()).limit(1).label("last_game_winner_id")


def getPositionJoin(fatherQuery):
    alias = aliased(User, name = "b")
    return userPositionQuery(alias, fatherQuery).label("position")

def getInternalPositionJoin(fatherQuery):
    alias = aliased(User, name = "c")
    return userInternalPositionQuery(alias, fatherQuery).label("internal_position")

#query utilizzate per le posizioni
#la fatherQuery è la query (o entità) a cui si appoggia tutto per il confronto
def userPositionQuery(user, fatherQuery):
    return db.session.query(func.count(distinct(user.score)) + 1).filter(fatherQuery.score < user.score)
def userInternalPositionQuery(user, fatherQuery):
    return db.session.query(func.count(user.score) + 1).filter(or_(fatherQuery.score < user.score, and_(fatherQuery.score == user.score, fatherQuery.username > user.username)))
