# -*- coding: utf-8 -*-
from app import app

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.base.models import Base, CommonPK
from app.game.models import partecipation

class User(Base, CommonPK):
  username = Column(String(250), nullable = False, unique = True)
  email = Column(String(250), nullable = False, unique = True)
  score = Column(Integer, default = app.config["DEFAULT_USER_SCORE"])
  games = relationship("Game", secondary = partecipation, back_populates = "users")

class Keychain(Base, CommonPK):

  user_id = Column(Integer, ForeignKey("user.id"), nullable = False)
  user = relationship("User")
  password = Column(String) #dovrà essere hashata
  facebookToken = Column(String)
