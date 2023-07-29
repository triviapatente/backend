# -*- coding: utf-8 -*-

from tp import app, db
from flask import g
from tp.auth.models import User
from tp.game.models import Game, Round, Question, ProposedQuestion, Partecipation
from tp.game.utils import getUsersFromGame, getWinner, updateScore
from tp.utils import doTransaction
from tp.cron.events import stimulate_daily, game_about_to_expire, game_expired
from tp.decorators import create_session

from datetime import datetime, timedelta
from sqlalchemy import func, or_

@create_session
def expire_matches():
    with app.app_context():
        stimulate_users()
        alert_age = app.config["MATCH_ALERT_AGE"]
        max_age = app.config["MATCH_MAX_AGE"]
        alert_thresold = datetime.utcnow() - timedelta(seconds=alert_age)
        expire_thresold = datetime.utcnow() - timedelta(seconds=max_age)
        print(f"[expire_matches Cron] Cron job with alert_thresold = {alert_thresold} and expire_thresold = {expire_thresold}")
        alert_games = Game.query.filter(Game.createdAt > expire_thresold).filter(Game.createdAt <= alert_thresold).filter(Game.ended == False, Game.pre_expiration_notified == False).all()
        print(alert_games)
        for game in alert_games:
            doTransaction(alert, game = game)
        db.session.commit()
        expired_games = Game.query.filter(Game.createdAt <= expire_thresold).filter(Game.ended == False).all()
        for game in expired_games:
            doTransaction(expire, game = game)
def stimulate_users():
    trigger_thresold = datetime.utcnow() - timedelta(days=1)
    lastGame = Partecipation.query.with_entities(func.max(Partecipation.createdAt)).filter(Partecipation.user_id == User.id).label("lastGame")
    users = User.query.filter(or_(lastGame == None, lastGame < trigger_thresold), or_(User.last_daily_stimulation == None, User.last_daily_stimulation < trigger_thresold)).all()
    for user in users:
        stimulate(user)
def stimulate(user):
    print(f"About to stimulate user {user.username}..")
    user.last_daily_stimulation = datetime.utcnow()
    stimulate_daily(user)
    db.session.add(user)
    db.session.commit()
def alert(game):
    print(f"[expire_matches.alert cron] Game: {game.id}")
    [userA, userB] = getUsersFromGame(game)
    game_about_to_expire(game, userA, userB)
    game_about_to_expire(game, userB, userA)
    game.pre_expiration_notified = True
    db.session.add(game)

def expire(game):
    print(f"[expire_matches.expire cron] Game: {game.id}")
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
    game_expired(game, userA, userB)
    game_expired(game, userB, userA)
    db.session.add(game)
