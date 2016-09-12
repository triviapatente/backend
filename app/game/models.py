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

class Round(Base, CommonPK):

  number = Column(Integer, nullable = False)
  game_id = Column(Integer, ForeignKey("game.id"), nullable = False)
  game = relationship("Game")

class Quiz(Base, CommonPK):

  question = Column(String(250), nullable = False)
  answer = Column(Boolean, nullable = False)
  image_id = Column(Integer, ForeignKey("image.id"))
  category_id = Column(Integer, ForeignKey("category.id"), nullable = False)
  image = relationship("Image")
  category = relationship("Category")

class Image(Base, CommonPK):

    image = Column(String(250)) #path dell'immagine, in alternativa: blob

class Category(Base, CommonPK):

  name = Column(String(250), nullable = False)
