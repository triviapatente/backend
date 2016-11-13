# -*- coding: utf-8 -*-
from tp import db
from flask import g
from tp.game.models import *
from sqlalchemy import func, distinct, and_
from sqlalchemy.orm import aliased
from tp import db
from datetime import datetime, timedelta
from utils import *

def getWrongLastQuestions(category_id):
    if not category_id:
        return None
    a = aliased(Question, name = "a")
    #SELECT max(a."createdAt") AS max_1 FROM question AS a WHERE question.quiz_id = a.quiz_id
    max_created = db.session.query(a).with_entities(func.max(a.createdAt)).filter(a.quiz_id == Question.quiz_id)
    #SELECT * FROM question
    #JOIN quiz ON quiz.id = question.quiz_id
    #WHERE question.user_id = g.user_id
    #AND quiz.category_id = category_id
    #AND question."createdAt" = max_created
    #AND quiz.answer != question.answer
    query = Question.query.join(Quiz).with_entities(Quiz).filter(Question.user_id == g.user.id).filter(Quiz.category_id == category_id).filter(Question.createdAt == max_created).filter(Quiz.answer != Question.answer)
    output = query.all()
    return output
#ottiene tutte le info del progresso di un utente in una category (wrong answers + chart progress)
# parametro: ##category_id: id della categoria, o None per riferirsi alla categoria complessiva
def getCategoryInfo(category_id):
    n = app.config["NUMBER_OF_CHART_DIVISORS"]
    end = datetime.now()
    start = end + timedelta(days = -n)
    output = {"success": True}
    output["progress"] = getProgressChart(category_id, n, start, end)
    if category_id:
        output["wrong_answers"] = getWrongLastQuestions(category_id)
    return output

def getProgressChart(category_id, n, start, end = datetime.now()):
    time_slice = (timestamp(end) - timestamp(start)) / n
    delta = timedelta(seconds = time_slice)
    output = {}
    cursor = start + delta
    while cursor <= end:
        output[cursor.isoformat()] = getPercentageIn(category_id, start, cursor)
        start += delta
        cursor += delta

    return output

def getPercentageIn(category_id, start, end):
    (correct, total) = getProgressValuesIn(category_id, start, end)
    if total == 0:
        return 0
        return correct * 100 / total

def getProgressValuesIn(category_id, start, end):
    a = aliased(Question, name = "a")
    b = aliased(Question, name = "b")
    c = aliased(Question, name = "c")

    #SELECT max(b."createdAt") AS max_1 FROM question AS b WHERE  a.quiz_id = b.quiz_id
    max_created = db.session.query(b).with_entities(func.max(b.createdAt)).filter(a.quiz_id == b.quiz_id)
    if start:
        #AND b."createdAt" > start
        max_created = max_created.filter(b.createdAt > start)
    if end:
        #AND b."createdAt" <= end
        max_created = max_created.filter(b.createdAt <= end)
    #SELECT count(DISTINCT c.quiz_id) FROM question AS c JOIN quiz ON quiz.id = c.quiz_id
    total_questions = db.session.query(c).with_entities(func.count(distinct(c.quiz_id))).join(Quiz)
    if category_id:
        #WHERE quiz.category_id = category.id
        total_questions = total_questions.filter(Quiz.category_id == category_id)
    #count(createdAt)
    correct_questions = func.count(a.createdAt)
    #SELECT  total_questions as total, correct_questions AS correct
    #FROM question AS a
    #JOIN quiz ON quiz.id = a.quiz_id
    #JOIN category ON category.id = quiz.category_id
    #WHERE a.user_id = g.user_id AND a."createdAt" = max_created
    query = db.session.query(a).join(Quiz).with_entities(correct_questions.label("correct"), total_questions.label("total")).filter(a.user_id == g.user.id).filter(a.createdAt == max_created).filter(a.answer == Quiz.answer)
    if category_id:
        #AND quiz.category_id = category.id
        query = query.join(Category).filter(Quiz.category_id == category_id)
    output = query.first()
    return (output.correct, output.total)

#ottiene le statistiche complessive
def getGeneralInfos():
    #nessuna category_id si traduce in complessivo
    #nessun range si traduce in totale
    (correct, total) = getProgressValuesIn(None, None, None)
    return {"id": None, "hint": "Complessivo", "total_answers": total, "correct_answers": correct}

def getCategoryPercentages(user):
    a = aliased(Question, name = "a")
    b = aliased(Question, name = "b")
    c = aliased(Question, name = "c")
    #SELECT max(v."createdAt") AS max_1 FROM question, question AS b WHERE b.quiz_id = a.quiz_id
    max_created = db.session.query(b).with_entities(func.max(b.createdAt)).filter(b.quiz_id == a.quiz_id)
    #SELECT count(DISTINCT c.quiz_id) FROM question AS c JOIN quiz ON quiz.id = c.quiz_id WHERE quiz.category_id = category.id
    total_questions = db.session.query(c).with_entities(func.count(distinct(c.quiz_id))).join(Quiz).filter(Quiz.category_id == Category.id).label("total_answers")
    #count(createdAt)
    correct_questions = func.count(a.createdAt).label("correct_answers")
    #SELECT category.id AS category_id, category.hint AS category_hint, correct_questions AS "correct_answers", total_questions  AS "total_answers"
    #FROM quiz
    #LEFT OUTER JOIN question AS a ON quiz.id = a.quiz_id AND quiz.answer = a.answer AND a."createdAt" = max_created AND a.user_id = 2
    #JOIN category ON category.id = quiz.category_id
    #GROUP BY category.id, category.hint
    #ORDER BY category.hint
    query = db.session.query(Quiz).join(a, and_(a.quiz_id == Quiz.id, a.answer == Quiz.answer, a.createdAt == max_created, a.user_id == user.id)).join(Category).with_entities(Category.id, Category.hint, correct_questions, total_questions).order_by(Category.hint).group_by(Category.id, Category.hint)
    output = query.all()
    general = getGeneralInfos()
    output.insert(0, general)
    return output
