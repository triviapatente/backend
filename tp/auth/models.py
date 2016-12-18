# -*- coding: utf-8 -*-
from tp import app

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum, Date, BigInteger
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context

from itsdangerous import (JSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from tp.base.models import Base, CommonPK
from werkzeug.utils import secure_filename
from validate_email import validate_email
from sqlalchemy.orm import validates
from datetime import datetime

import os

class User(Base, CommonPK):
  #valori identificativi dell'utente, devono essere unici
  username = Column(String, nullable = False, unique = True)
  email = Column(String(250), nullable = False, unique = True)

  @validates("email")
  def validate_email(self, key, value):
      assert validate_email(value)
      return value

  #dati personali dell'utente
  name = Column(String)
  surname = Column(String)
  #path dell'immagine
  image = Column(String)
  #data di nascita
  birth = Column(Date)
  #punteggio di partenza del giocatore
  score = Column(Integer, default = app.config["DEFAULT_USER_SCORE"])
  #partite giocate dal giocatore
  games = relationship("Partecipation", back_populates = "user")
  export_properties = ["position", "last_game_won"]
  #metodo che permette di modificare il nome dell'immagine adattandolo al nome utente in modo sicuro
  def getFileName(self, filename):
      #se il file è permesso
      if User.allowed_file(filename):
          #lo sostituisco con lo username, mantenendo l'ultima estensione e lo rendo sicuro
          return secure_filename(str(self.username) + "." + str(filename.rsplit('.')[-1]))
      else:
          return False

  #proprietà che definisce quando un file è permesso o no
  @staticmethod
  def allowed_file(filename):
      return '.' in filename and filename.rsplit('.')[-1] in app.config["ALLOWED_EXTENSIONS"]

class FacebookToken(Base, CommonPK):
  #utente che possiede il token
  user_id = Column(Integer, ForeignKey("user.id"), nullable = False, unique = True)
  user = relationship("User")
  #id di facebook dell'utente
  fb_id = Column(BigInteger, nullable = False, unique = True)
  expiration = Column(Date, nullable = False)
  token = Column(String, nullable = False)

  @staticmethod
  def getFrom(user, token, tokenInfos):
      output = FacebookToken(user_id = user.id)
      data = tokenInfos["data"]
      if data["is_valid"] == False:
          raise FBTokenNotValidException()
      output.fb_id = data["user_id"]
      output.expiration = datetime.fromtimestamp(data["expires_at"])
      output.token = token
      return output


class Keychain(Base, CommonPK):
  #utente che possiede il keychain
  user_id = Column(Integer, ForeignKey("user.id"), nullable = False, unique = True)
  user = relationship("User")

  lifes = Column(Integer, nullable = False)

  password = Column(String)
  #nonce per permettere l'invalidazione anticipata del token
  nonce = Column(String)

  #TODO: put token inside Installation
  #TODO: il token tiene conto del tempo, e gli serve per calcolare l'expiration

  #proprietà che contiene un auth token, utile per l'autenticazione
  #l'expiration time è settato di default a un mese
  @property
  def auth_token(self):
      #ottengo il serializer
      s = self.getSerializer()
      #critto l'id dell'utente proprietario del keychain e il nonce e ne ottengo un token
      return s.dumps({ 'id': self.user_id, 'nonce': self.nonce})

  #metodo centrale che contiene l'istanza del serializer per generazione e verifica di token
  #muovendolo in un metodo centrale siamo sicuri che la chiave usata per generare/verificare è sempre la stessa
  @staticmethod
  def getSerializer():
      return Serializer(app.config['SECRET_KEY'])

  #metodo statico che analizza e verifica un token, indicando se la sessione è ancora attiva
  @classmethod
  def verify_auth_token(self, token):
      #ottengo il serializer
      s = self.getSerializer()
      user = None
      try:
          #vedo se riesco a verificare il token
          data = s.loads(token)
          user = User.query.get(data['id'])
          #vedo se il token non è scaduto (controllo il nonce)
          if Keychain.query.filter_by(user_id = user.id).first().nonce != data['nonce']:
              # se lo è setto l'utente a None
              user = None
      #se non riesco ritorno None
      except:
          user = None
      # ritorno l'utente
      return user

  #metodo che salva in password l'hash della password passata
  def hash_password(self, password):
      self.password = pwd_context.encrypt(password)

  #metodo che salva genera, hasha e salva un nuovo nonce di lunghezza ##length numeri consecutivi (in media di 2/3 cifre)
  def renew_nonce(self, length = 16):
      self.nonce = ''.join(str(x) for x in map(ord, os.urandom(length)))

  #metodo che controlla se la password candidata è equivalente all'hash salvato
  def check_password(self, candidate):
      return pwd_context.verify(candidate, self.password)
