# -*- coding: utf-8 -*-
from tp.events.decorators import event
from tp.events.utils import EventActions

@event("message", action = EventActions.create, preferences_key = "notification_message")
def send_message(room, message):
    data = {"message": message.json}
    return (room, data)
