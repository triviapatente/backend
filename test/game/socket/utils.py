# -*- coding: utf-8 -*-

from tp.game.models import Category, Quiz
from tp import db
#metodo che genera un set fittizio di categorie e quiz per non evocare il vero e proprio crawler a ogni test
def dumb_crawler():
    for i in range(0, 10):
        c = Category(name= "category_%d" % i)
        db.session.add(c)
        db.session.commit()
        for n in range(0, 40):
            q = Quiz(category_id = c.id, question = "Quiz %d della categoria %d" % (n, i), answer = (n % 2 == 0))
            db.session.add(q)
        db.session.commit()

def generate_random_category():
    c = Category(name= "category_100")
    db.session.add(c)
    db.session.commit()
    return c

def generate_random_question(category_id):
    q = Quiz(question= "question x", answer = True, category_id = category_id)
    db.session.add(q)
    db.session.commit()
    return q
