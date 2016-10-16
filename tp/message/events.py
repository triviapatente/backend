# -*- coding: utf-8 -*-
from tp.events.decorators import event
from tp.events.utils import EventActions

@event("message", action = EventActions.create, include_self = True, preferences_key = "notification_message")
def event_message(room, message):
    data = {"message": message.json}
    return (room, data)
