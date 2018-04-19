# -*- coding: utf-8 -*-

from tp import app, db
from flask import g
from tp.game.models import Game, Round, Question, ProposedQuestion
from tp.game.utils import getUsersFromGame, getWinner, updateScore
from tp.utils import doTransaction
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
            doTransaction(alert, game = game)
        db.session.commit()
        expired_games = Game.query.filter(Game.createdAt <= expire_thresold).filter(Game.ended == False).all()
        for game in expired_games:
            doTransaction(expire, game = game)

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
    #non importante, può essere qualsiasi dei due
    g.user = userA
    if game.started == True:
        lastRound = Round.query.filter(Round.game_id == game.id, Round.cat_id is not None).order_by(Round.number.desc()).first()
        questions = ProposedQuestion.query.filter(ProposedQuestion.round_id == lastRound.id).all()
        for q in questions:
            baseQuery = Question.query.filter(Question.round_id == lastRound.id, Question.quiz_id == q.quiz_id)
            userAQuery = baseQuery.filter(Question.user_id == userA.id)
            userBQuery = baseQuery.filter(Question.user_id == userB.id)
            if userAQuery.count() == 0:
                db.session.add(Question(round_id = lastRound.id, quiz_id = q.quiz_id, user_id = userA.id, answer = None))
            if userBQuery.count() == 0:
                db.session.add(Question(round_id = lastRound.id, quiz_id = q.quiz_id, user_id = userB.id, answer = None))
        updateScore(game)
    game.ended = True
    game.expired = True
    winner = getWinner(game)
    if winner is not None:
        game.winner_id = winner.id
    #events.game_expired(game, userA, userB)
    #events.game_expired(game, userB, userA)
    db.session.add(game)
