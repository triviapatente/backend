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

# get next n messages from ##offset of a room
def getMessages(game, offset):
    return jsonify(Message.query.order_by(Message.updatedAt).slice(offset, app.config["MESSAGE_PER_SCROLL"]).all())
