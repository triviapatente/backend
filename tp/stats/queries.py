# -*- coding: utf-8 -*-
from tp import db
from flask import g
from tp.game.models import *
from sqlalchemy import func, distinct, and_
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import case
from tp import db
from datetime import datetime, timedelta, date
from utils import *
import pytz

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
    tz = pytz.timezone('Europe/Rome')
    now = datetime.now(tz = tz)
    end = datetime(now.year, now.month, now.day)
    start = end + timedelta(days = -n)
    output = {"success": True}
    output["progress"] = getProgressChart(category_id, n, start, end, tz)
    if category_id:
        output["wrong_answers"] = getWrongLastQuestions(category_id)
    return output

def getProgressChart(category_id, n, start, end, tz = pytz.timezone('Europe/Rome')):
    time_slice = (timestamp(end, tz) - timestamp(start, tz)) / n
    delta = timedelta(seconds = time_slice)
    output = {}
    cursor = end
    while cursor >= start:
        (correct, total) = getProgressValuesIn(category_id, cursor)
        date = cursor.replace(tzinfo = tz).isoformat()
        output[date] = {"correct_answers": correct, "total_answers": total}
        cursor -= delta

    return output

def getProgressValuesIn(category_id, day):
    a = aliased(Question, name = "a")
    b = aliased(Question, name = "b")

    max_created = db.session.query(b).with_entities(func.max(b.createdAt)).filter(a.quiz_id == b.quiz_id, a.user_id == b.user_id)
    if day:
        max_created = max_created.filter(func.date_trunc('day', func.timezone("CEST", b.createdAt)) == func.date_trunc('day', day))
    total_questions = func.count(Quiz.id).label("total")
    correct_questions = func.sum(case([(a.answer == Quiz.answer, 1)], else_ = 0)).label("correct")
    query = Quiz.query.with_entities(total_questions, correct_questions).join(a).filter(a.user_id == g.user.id, a.createdAt == max_created)
    if category_id:
        #AND quiz.category_id = category.id
        query = query.filter(Quiz.category_id == category_id)
    output = query.first()
    return (output.correct, output.total)

#ottiene le statistiche complessive
def getGeneralInfos():
    #nessuna category_id si traduce in complessivo
    #nessun range si traduce in totale
    (correct, total) = getProgressValuesIn(None, None)
    return {"id": None, "hint": "Complessivo", "total_answers": total, "correct_answers": correct}

def getCategoryPercentages(user):
    a = aliased(Question, name = "a")
    b = aliased(Question, name = "b")
    c = aliased(Question, name = "c")
    d = aliased(Quiz, name = "d")
    #SELECT max(v."createdAt") AS max_1 FROM question, question AS b WHERE b.quiz_id = a.quiz_id
    max_created = db.session.query(b).with_entities(func.max(b.createdAt)).filter(b.quiz_id == a.quiz_id)
    #SELECT count(DISTINCT c.quiz_id) FROM question AS c JOIN quiz ON quiz.id = c.quiz_id WHERE quiz.category_id = category.id
    total_questions = db.session.query(c).with_entities(func.count(distinct(c.quiz_id))).join(Quiz).filter(Quiz.category_id == Category.id).label("total_answers")

    total_quizzes = db.session.query(d).with_entities(func.count(d.createdAt)).filter(Category.id == d.category_id).label("total_quizzes")
    correct_questions = func.count(a.createdAt).label("correct_answers")
    #SELECT category.id AS category_id, category.hint AS category_hint, correct_questions AS "correct_answers", total_questions  AS "total_answers"
    #FROM quiz
    #LEFT OUTER JOIN question AS a ON quiz.id = a.quiz_id AND quiz.answer = a.answer AND a."createdAt" = max_created AND a.user_id = 2
    #JOIN category ON category.id = quiz.category_id
    #GROUP BY category.id, category.hint
    #ORDER BY category.hint
    query = db.session.query(Quiz).outerjoin(a, and_(a.quiz_id == Quiz.id, a.answer == Quiz.answer, a.createdAt == max_created, a.user_id == user.id)).join(Category, Category.id == Quiz.category_id).with_entities(Category.id, Category.hint, correct_questions, total_questions, total_quizzes).order_by(Category.hint).group_by(Category.id, Category.hint)
    print query
    output = query.all()
    general = getGeneralInfos()
    categoryPercentages = []
    general_total_quizzes = 0
    for (id, hint, correct_answers, total_answers, total_quizzes) in output:
        general_total_quizzes += total_quizzes
        categoryPercentages.append({'id': id, 'hint': hint, 'correct_answers': correct_answers, 'total_answers': total_answers, "total_quizzes": total_quizzes})
    general["total_quizzes"] = general_total_quizzes
    categoryPercentages.insert(0, general)
    return categoryPercentages
