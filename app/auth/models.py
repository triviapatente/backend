# -*- coding: utf-8 -*-
from app import app

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from app.base.models import Base, CommonPK
from app.game.models import partecipation

class User(Base, CommonPK):
  #valori identificativi dell'utente, devono essere unici
  username = Column(String, nullable = False, unique = True)
  email = Column(String(250), nullable = False, unique = True)
  #dati personali dell'utente
  name = Column(String)
  surname = Column(String)
  #path dell'immagine
  image = Column(String)
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

  lifes = Column(Integer, nullable = False)
  #TODO: aggiungere controllo, uno dei due tra password o facebookToken deve essere sempre settato

  password = Column(String)
  #facebookToken dell'utente
  facebookToken = Column(String)

  #proprietà che contiene un auth token, utile per l'autenticazione
  #l'expiration time è settato di default a un mese
  @property
  def auth_token(self, expiration = 60 * 60 * 24 * 30):
      #ottengo il serializer
      s = self.getSerializer(expiration)
      #critto l'id dell'utente proprietario del keychain e ne ottengo un token
      return s.dumps({ 'id': self.user_id })

  #metodo centrale che contiene l'istanza del serializer per generazione e verifica di token
  #muovendolo in un metodo centrale siamo sicuri che la chiave usata per generare/verificare è sempre la stessa
  @staticmethod
  def getSerializer(expiration = None):
      return Serializer(app.config['SECRET_KEY'], expires_in = expiration)

  #metodo statico che analizza e verifica un token, indicando se la sessione è ancora attiva
  @classmethod
  def verify_auth_token(self, token):
      #ottengo il serializer
      s = self.getSerializer()
      try:
          #vedo se riesco a verificare il token
          data = s.loads(token)
      #se non riesco ritorno null
      except:
          return None
      #se no torno l'utente associato
      return User.query.get(data['id'])

  #metodo che salva in password l'hash della password passata
  def hash_password(self, password):
      self.password = pwd_context.encrypt(password)
  #metodo che controlla se la password candidata è equivalente all'hash salvato
  def check_password(self, candidate):
      return pwd_context.verify(candidate, self.password)
