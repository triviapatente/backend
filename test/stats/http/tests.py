# -*- coding: utf-8 -*-
from tp.game.models import Question, Game, Round, Quiz, Category
from test.game.socket.utils import dumb_crawler
from test.game.http.api import new_game
from test.auth.http.api import register
from test.shared import TPAuthTestCase
from tp import db
from api import *
class StatsHTTPTestCase(TPAuthTestCase):
    quiz_1 = None
    quiz_2 = None
    quiz_3 = None
    quiz_4 = None

    def setUp(self):
        super(StatsHTTPTestCase, self).setUp()
        dumb_crawler()
        cat1 = db.session.query(Category).filter(Category.id == 1).one()
        cat2 = db.session.query(Category).filter(Category.id == 2).one()
        self.quiz_1 = db.session.query(Quiz).filter(Quiz.category_id == 1).first()
        self.quiz_2 = db.session.query(Quiz).filter(Quiz.category_id == 1).all()[1]
        self.quiz_3 = db.session.query(Quiz).filter(Quiz.category_id == 2).first()
        self.quiz_4 = db.session.query(Quiz).filter(Quiz.category_id == 2).all()[1]
        #Getting rid of the object out of session errors
        db.session.expunge(cat1)
        db.session.expunge(cat2)
        db.session.expunge(self.quiz_1)
        db.session.expunge(self.quiz_2)
        db.session.expunge(self.quiz_3)
        db.session.expunge(self.quiz_4)

        user_id = self.user.get("id")
        opponent_user_id = register(self, "a", "a@a.it", "a").json.get("user").get("id")
        game_id = new_game(self, opponent_user_id).json.get("game").get("id")
        r1 = Round(number = 1, dealer_id = user_id, game_id = game_id, cat_id = 1)
        r2 = Round(number = 2, dealer_id = user_id, game_id = game_id, cat_id = 2)
        db.session.add(r1)
        db.session.add(r2)

        db.session.commit()

        q1 = Question(round_id = r1.id, user_id = user_id, quiz_id = self.quiz_1.id, answer = not self.quiz_1.answer) #SBAGLIATO
        q2 = Question(round_id = r1.id, user_id = user_id, quiz_id = self.quiz_2.id, answer = self.quiz_2.answer) #GIUSTO
        q3 = Question(round_id = r1.id, user_id = user_id, quiz_id = self.quiz_3.id, answer = not self.quiz_3.answer) #SBAGLIATO
        q4 = Question(round_id = r1.id, user_id = user_id, quiz_id = self.quiz_4.id, answer = not self.quiz_4.answer) #SBAGLIATO
        q5 = Question(round_id = r2.id, user_id = user_id, quiz_id = self.quiz_3.id, answer = self.quiz_3.answer) #GIUSTO, mi correggo

        #INSTANTI DI TEMPO DIFFERENTI
        db.session.add(q1)
        db.session.commit()
        db.session.add(q2)
        db.session.commit()
        db.session.add(q3)
        db.session.commit()
        db.session.add(q4)
        db.session.commit()
        db.session.add(q5)
        db.session.commit()


    def test_get_categories(self):
        print "#1 Risposta successful"
        response = get_categories(self)
        assert response.json.get("success") == True
        print "#2 Le categorie ci sono e sono tutte"
        categories = response.json.get("categories")
        assert categories != None
        assert len(categories) == Category.query.count()

    def test_get_progresses(self):
        print "#1 Risposta successful"
        response_cat_1 = get_progresses(self, 1)
        assert response_cat_1.json.get("success") == True

        print "#2 risposta coerente con le domande a cui ho risposto"
        response_cat_2 = get_progresses(self, 2)
        print "#2.1 Categoria 1"
        progress_1 = response_cat_1.json.get("progress")
        length = len(progress_1)
        assert length
        keys = sorted(progress_1.keys())
        last_key = keys[-1]
        last_progress = progress_1[last_key]
        assert last_progress
        assert last_progress.get("percentage") == 50
        print "#2.2 Categoria 2"
        progress_2 = response_cat_2.json.get("progress")
        length = len(progress_2)
        assert length
        keys = sorted(progress_2.keys())
        last_key = keys[-1]
        last_progress = progress_2[last_key]
        assert last_progress
        assert last_progress.get("percentage") == 50

    def test_get_wrong_answers(self):
        print "#1 Risposta successful"
        response_cat_1 = get_wrong_answers(self, 1)
        assert response_cat_1.json.get("success") == True
        assert response_cat_1.json.get("answers") != None

        print "#2 risposta coerente con le domande a cui ho risposto"
        response_cat_2 = get_wrong_answers(self, 2)
        print "#2.1 Categoria 1"
        answers_1 = response_cat_1.json.get("answers")
        assert len(answers_1) == 1
        assert answers_1[0].get("quiz_id") == self.quiz_1.id
        print "#2.2 Categoria 2"
        answers_2 = response_cat_2.json.get("answers")
        assert len(answers_2) == 1
        assert answers_2[0].get("quiz_id") == self.quiz_4.id
