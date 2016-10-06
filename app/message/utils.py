# -*- coding: utf-8 -*-

from app.message.models import *
from app import app, db

# save ##message from ##user to room(##game)
def saveMessage(user, game, message):
    try:
        new_message = Message(user = user, game = game, content = message)
        db.session.add(new_message)
        db.session.commit()
        return new_message
    except:
        return False

# get next n messages after ##datetime of a room (##game_id)
def getMessages(game_id, datetime):
    # filter by updatedAt and ##game_id
    query = Message.query.filter(Message.game_id == game_id, Message.updatedAt < datetime)
    # get message ordered by updatedAt field
    query = query.order_by(Message.updatedAt).limit(app.config["MESSAGE_PER_SCROLL"])
    return query.all()
