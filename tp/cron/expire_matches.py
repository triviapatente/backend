# -*- coding: utf-8 -*-

from tp import app, db
from tp.game.models import Game
from tp.game.utils import getUsersFromGame
from tp.cron import events
from datetime import datetime, timedelta
def expire_matches():
    with app.app_context():
        alert_age = app.config["MATCH_ALERT_AGE"]
        max_age = app.config["MATCH_MAX_AGE"]
        alert_thresold = datetime.utcnow() - timedelta(seconds=alert_age)
        expire_thresold = datetime.utcnow() - timedelta(seconds=max_age)
        print "[expire_matches Cron] Cron job with alert_thresold = %s and expire_thresold = %s" % (alert_thresold, expire_thresold)
        alert_games = Game.query.filter(Game.createdAt > expire_thresold).filter(Game.createdAt <= alert_thresold).filter(Game.ended == False, Game.pre_expiration_notified == False).all()
        print alert_games
        for game in alert_games:
            alert(game)
        db.session.commit()
        expired_games = Game.query.filter(Game.createdAt <= expire_thresold).filter(Game.ended == False).all()
        for game in expired_games:
            expire(game)

def alert(game):
    print "[expire_matches.alert cron] Game: %d" % game.id
    [userA, userB] = getUsersFromGame(game)
    events.game_about_to_expire(game, userA, userB)
    events.game_about_to_expire(game, userB, userA)
    game.pre_expiration_notified = True
    db.session.add(game)

def expire(game):
    print "[expire_matches.expire cron] Game: %d" % game.id
    [userA, userB] = getUsersFromGame(game)
    #lastRound = pass
    #last round need to be filled with empty answers
    game.ended = True
    game.expired = True
    #set winner
    events.game_expired(game, userA, userB)
    events.game_expired(game, userB, userA)
    db.session.add(game)
