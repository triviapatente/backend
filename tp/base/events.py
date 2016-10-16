# -*- coding: utf-8 -*-
from tp.events.decorators import event
from tp.events.utils import EventActions
from tp.base.utils import getRoomsFor, RoomType
from flask import g

@event("user_joined", action = EventActions.joined, include_self = False, needs_push = False)
def user_joined(room):
    data = {"user": g.user.json}
    return (room, data)

@event("user_left", action = EventActions.left, include_self = False, needs_push = False)
def user_left(room):
    data = {"user": g.user.json}
    return (room, data)
