# -*- coding: utf-8 -*-
from flask import g
from tp.auth.models import User
from tp.game.models import Partecipation
from tp.rank.queries import getUserPosition

# enumeration of room type
from enum import Enum
class RoomType(Enum):
    game = "game"
#metodo che a partire da un id di room e di un tipo di room, ne costruisce il nome
def roomName(id, type):
    if isinstance(type, RoomType):
        type = type.value
    return "%s_%s" % (type, id)

def getInfosFromRoom(id):
    parts = id.split("_")
    if parts and len(parts) == 2:
        type = parts[0]
        id = parts[1]
        return (RoomType.__members__.get(type), id)
    return (None, None)

#ottiene gli utenti di una room in base al tipo
#se la room non è conosciuta ritorna None
#se check_for_user è True ritorna solo il mio utente, se è presente nella room
def getUsersFromRoom(type, game_id, check_for_user = False):
    #unico caso al momento, ma in caso di riutilizzo del sistema room ci saranno altri casi
    if type == RoomType.game.value:
        query = User.query.join(Partecipation).filter(Partecipation.game_id == game_id)
        if check_for_user:
            query.filter(User.id == g.user.id)
        return query.all()
    return None

def getRoomsFor(type, user):
    rooms = []
    if type == RoomType.game:
        rooms = Game.query.with_entities(Game.id).join(User).filter(User.id == user.id)
    return [roomName(id, type) for id in rooms]

def get_connection_values(user):
    if not user:
        return {}
    output = {}
    output["global_rank_position"] = getUserPosition(user)
    #output["stats"] = getCategoryPercentages(user)
    #output["preferences"] = getPreferencesFromUser(user)
    #output["fb"] = getFBTokenInfosFromUser(user)
    return output
