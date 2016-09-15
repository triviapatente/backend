# -*- coding: utf-8 -*-
from app import app

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

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

  password = Column(String)
  #facebookToken dell'utente
  facebookToken = Column(String)

  #proprietà che contiene un auth token, utile per l'autenticazione
  @property
  def auth_token(self, expiration = 60 * 60 * 24 * 30):
      s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
      return s.dumps({ 'id': self.id })
  #metodo che salva in password l'hash della password passata
  def hash_password(self, password):
      password = pwd_context.encrypt(password)
  #metodo che controlla se la password candidata è equivalente all'hash salvato
  def check_password(self, candidate):
      return pwd_context.verify(candidate, self.password)
