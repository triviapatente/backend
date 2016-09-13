# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table, Boolean
from sqlalchemy.orm import relationship

from app.base.models import Base, CommonPK


partecipation = Table('partecipation', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key = True),
    Column('game_id', Integer, ForeignKey('game.id'), primary_key = True)
)

class Game(Base, CommonPK):
  users = relationship("User", secondary = partecipation, back_populates = "games")
  game_id = Column(Integer, ForeignKey("user.id"), nullable = False)
  winner = relationship("User", back_populates = "games_won")

#un round adesso rappresenta il round di un utente, e contiene tutte le info di quel round, come utente che sta giocando, categoria che ha scelto, game di appartenenza, domande proposte
class Round(Base):
  number = Column(Integer, nullable = False)
  game_id = Column(Integer, ForeignKey("game.id"), nullable = False, primary_key = True)
  game = relationship("Game")
  user_id = Column(Integer, ForeignKey("user.id"), nullable = False, primary_key = True)
  user = relationship("User")
  cat_id = Column(Integer, ForeignKey("category.id"), nullable = False)
  chosen_category = relationship("Category")
  questions = relationship("Question", back_populates = "round")

class Quiz(Base, CommonPK):

  question = Column(String(250), nullable = False)
  answer = Column(Boolean, nullable = False)
  image_id = Column(Integer, ForeignKey("image.id"))
  category_id = Column(Integer, ForeignKey("category.id"), nullable = False)
  image = relationship("Image")
  category = relationship("Category")

class Question(Base):
  quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable = False, primary_key = True)
  quiz = relationship("Quiz")
  answer = Column(Boolean, nullable = False)
  round_id = Column(Integer, ForeignKey("quiz.id"), nullable = False, primary_key = True)
  round = relationship("Round", back_populates = "questions")

class Image(Base, CommonPK):
  image = Column(String) #path dell'immagine, in alternativa: blob

class Category(Base, CommonPK):
  name = Column(String(250), nullable = False)
