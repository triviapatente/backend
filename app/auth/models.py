# -*- coding: utf-8 -*-
from app import app

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.base.models import Base, CommonPK
from app.game.models import partecipation

class User(Base, CommonPK):
  #valori identificativi dell'utente, devono essere unici
  username = Column(String(250), nullable = False, unique = True)
  email = Column(String(250), nullable = False, unique = True)
  #punteggio di partenza del giocatore
  score = Column(Integer, default = app.config["DEFAULT_USER_SCORE"])
  #partite giocate dal giocatore
  games = relationship("Game", secondary = partecipation, back_populates = "users")
  #partite vinte dal giocatore
  games_won = relationship("Game", back_populates = "winner")

class Keychain(Base, CommonPK):
  #utente che possiede il keychain
  user_id = Column(Integer, ForeignKey("user.id"), nullable = False)
  user = relationship("User")
  #TODO: aggiungere controllo, uno dei due tra password o facebookToken deve essere sempre settato
  #TODO: password dell'utente, dovrà essere salvata hashata
  password = Column(String)
  #facebookToken dell'utente
  facebookToken = Column(String)
