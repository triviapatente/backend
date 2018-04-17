# -*- coding: utf-8 -*-
from enum import Enum
from tp.base.utils import getInfosFromRoom, getUsersFromRoom
class EventActions(Enum):
    create = "create"
    update = "update"
    destroy = "destroy"
    joined = "joined"
    left = "left"
    invited = "invited"
    answer = "answer"
    game_left = "game_left"
    message = "message"
    notify = "notify"
    expired = "expired"

def getUsersFromRoomID(room):
    (type, id) = getInfosFromRoom(room)
    return getUsersFromRoom(type.value, id)
