# -*- coding: utf-8 -*-
from flask import Blueprint, g, jsonify
from tp.decorators import auth_required, needs_values
from tp.rank.queries import *

rank = Blueprint("rank", __name__, url_prefix = "/rank")

#api per la richiesta della classifica italiana (globale)
@rank.route("/global", methods = ["GET"])
@auth_required
def getItalianRank():
    #chiedo la classifica (elenco utenti ordinato in base al punteggio) dei primi n utenti
    rank = getRank()
    print "User %s got global rank." % g.user.username
    return jsonify(rank = rank, my_position = getUserPosition(g.user))

@rank.route("/friends", methods = ["GET"])
@auth_required
def getFriendsRank():
    pass

@rank.route("/search", methods = ["GET"])
@auth_required
@needs_values("GET", "query")
def searchInRank():
    query = g.query["query"]
    matches = search("%" + query + "%")
    return jsonify(matches = matches)
