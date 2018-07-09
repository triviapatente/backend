# -*- coding: utf-8 -*-
from flask import g
from tp import app, db
from tp.auth.models import *
from tp.game.utils import getTrainingStats
from tp.game.models import Partecipation
from tp.events.models import *
from tp.rank.queries import getUserPosition
from tp.stats.queries import getCategoryPercentages

# enumeration of room type
from enum import Enum
class RoomType(Enum):
    game = "game"
#metodo che a partire da un id di room e di un tipo di room, ne costruisce il nome
def roomName(id, type):
    if isinstance(type, RoomType):
        type = type.value
    return "%s_%s" % (type, id)

def getUsersFromRoomID(room):
    (type, id) = getInfosFromRoom(room)
    return getUsersFromRoom(type.value, id)


def getInfosFromRoom(id):
    parts = id.split("_")
    if parts and len(parts) == 2:
        type = parts[0]
        id = parts[1]
        return (RoomType.__members__.get(type), id)
    return (None, None)

def jsonifyDates(json):
    keys = ["createdAt", "updatedAt", "last_daily_stimulation", "last_game_friend_ended_game_stimulation"]
    for key in keys:
        if key in json and json[key] is not None:
            json[key] = str(json[key])
    return json
#ottiene gli utenti di una room in base al tipo
#se la room non è conosciuta ritorna None
#se check_for_user è True ritorna solo il mio utente, se è presente nella room
def getUsersFromRoom(type, game_id, check_for_user = False):
    #unico caso al momento, ma in caso di riutilizzo del sistema room ci saranno altri casi
    if type == RoomType.game.value:
        query = User.query.join(Socket).join(RoomParticipation).filter(RoomParticipation.game_id == game_id)
        if check_for_user:
            query.filter(User.id == g.user.id)
        return query.all()
    return None

def dropUser(id):
    user = User.query.filter(User.id == id).one()
    user.generateMockUsername()
    user.generateMockEmail()
    user.name = None
    user.surname = None
    user.score = 0
    if user.image:
        try:
            os.remove(user.image)
        except:
            pass
    user.image = None
    Keychain.query.filter(Keychain.user_id == id).delete()
    Socket.query.filter(Socket.user_id == id).delete()
    Installation.query.filter(Installation.user_id == id).delete()
    RoomParticipation.query.filter(RoomParticipation.user_id == id).delete()
    games = Game.query.join(Partecipation).filter(Partecipation.user_id == id).all()
    for game in games:
        game.expired = True
        game.ended = True
        db.session.add(game)

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
    output["privacy_policy_last_update"] = app.config["PRIVACY_POLICY_LAST_UPDATE"]
    output["terms_and_conditions_last_update"] = app.config["TERMS_AND_CONDITIONS_LAST_UPDATE"]
    output["training_stats"] = getTrainingStats()
    output["stats"] = getCategoryPercentages(user)
    output["match_max_age"] = app.config["MATCH_MAX_AGE"]
    #output["preferences"] = getPreferencesFromUser(user)
    #output["fb"] = getFBTokenInfosFromUser(user)
    return output
