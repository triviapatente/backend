# -*- coding: utf-8 -*-
from tp import app
import sys

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum, Date, BigInteger
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context

from itsdangerous import (JSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from tp.base.models import Base, CommonPK
from werkzeug.utils import secure_filename
from validate_email import validate_email
from sqlalchemy.orm import validates
from tp.exceptions import *
from datetime import datetime

import os

MAX_CHARS = app.config["MAX_CHARS_FOR_FIELD"]

class User(Base, CommonPK):
  #valori identificativi dell'utente, devono essere unici
  username = Column(String(MAX_CHARS), nullable = False, unique = True)
  email = Column(String(MAX_CHARS), nullable = False, unique = True)

  @validates("email")
  def validate_email(self, key, value):
      if not validate_email(value):
          raise BadParameters(["email"])
      if " " in value:
          raise BadParameters(["email", "La email non deve contenere spazi"])
      return value
  @validates("username")
  def validate_username(self, key, value):
      min_length = app.config["USERNAME_MIN_CHARS"]
      if len(value) < min_length:
          raise BadParameters(["username"], "L'username deve contenere almeno 2 caratteri")
      if " " in value:
          raise BadParameters(["username", "L'username non deve contenere spazi"])
      return value
  #dati personali dell'utente
  name = Column(String(MAX_CHARS))
  surname = Column(String(MAX_CHARS))
  #path dell'immagine
  image = Column(String)
  #data di nascita
  birth = Column(Date)
  #punteggio di partenza del giocatore
  score = Column(Integer, default = app.config["DEFAULT_USER_SCORE"])
  #partite giocate dal giocatore
  games = relationship("Partecipation", back_populates = "user")
  export_properties = ["position", "last_game_won", "internalPosition"]
  #metodo che permette di modificare il nome dell'immagine adattandolo al nome utente in modo sicuro
  def getFileName(self, filename):
      #se il file è permesso
      if User.allowed_file(filename):
          #lo sostituisco con lo username, mantenendo l'ultima estensione e lo rendo sicuro
          return secure_filename(str(self.username) + "." + str(filename.rsplit('.')[-1]))
      else:
          return False

  def getUsernameCounter(self, candidate):
      start = len(candidate)
      suffix = self.username[start:]
      if suffix.isdigit():
          return int(suffix)
      return None

  def generateUsername(self):
      if self.name and self.surname:
          candidate = self.name.lower() + self.surname.lower()
          matches = User.query.filter(User.username.like(candidate + "%")).order_by(User.username.asc()).all()
          if len(matches) == 0:
              self.username = candidate
          else:
              counters = [user.getUsernameCounter(candidate) for user in matches]
              max_counter = max(counters)
              if max_counter is None:
                  counter = 1
              else:
                  counter = max(counters) + 1
              self.username = "%s%d" % (candidate, counter)

  #proprietà che definisce quando un file è permesso o no
  @staticmethod
  def allowed_file(filename):
      return '.' in filename and filename.rsplit('.')[-1] in app.config["ALLOWED_EXTENSIONS"]

  @property
  def displayName(self):
      if self.name is not None and self.surname is not None:
          return "%s %s" %(self.name, self.surname)
      return self.username
      
class FacebookToken(Base, CommonPK):
  #utente che possiede il token
  user_id = Column(BigInteger, ForeignKey("user.id"), nullable = False, unique = True)
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
      output.setExpiration(data["expires_at"])
      output.token = token
      return output

  def setExpiration(self, expiration):
      self.expiration = datetime.fromtimestamp(expiration)


class Keychain(Base, CommonPK):
  #utente che possiede il keychain
  user_id = Column(BigInteger, ForeignKey("user.id"), nullable = False, unique = True)
  user = relationship("User")

  lifes = Column(Integer, nullable = False)

  @validates("password")
  def validate_password(self, key, value):
      min_length = app.config["PASSWORD_MIN_CHARS"]
      if len(value) < min_length:
          raise BadParameters(["password"], "La password deve contenere almeno 7 caratteri")
      return value

  password = Column(String)
  #nonce per permettere l'invalidazione anticipata del token
  nonce = Column(String)
  #nonce che permette di invalidare un password_token quando è usato
  change_password_nonce = Column(String)

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
  @property
  def change_password_token(self):
      #ottengo il serializer
      s = self.getSerializer()
      #critto l'id dell'utente proprietario del keychain
      return s.dumps({ 'id': self.user_id, 'nonce': self.change_password_nonce})

  #metodo centrale che contiene l'istanza del serializer per generazione e verifica di token
  #muovendolo in un metodo centrale siamo sicuri che la chiave usata per generare/verificare è sempre la stessa
  @staticmethod
  def getSerializer():
      return Serializer(app.config['SECRET_KEY'])

  #metodo statico che analizza e verifica un token, indicando se la sessione è ancora attiva
  @classmethod
  def verify_auth_token(self, token, nonce_key = "nonce"):
      #ottengo il serializer
      s = self.getSerializer()
      user = None
      try:
          #vedo se riesco a verificare il token
          data = s.loads(token)
          user = User.query.get(data['id'])
          #vedo se il token non è scaduto (controllo il nonce)
          nonce = Keychain.query.filter_by(user_id = user.id).first()[nonce_key]
          if nonce != data['nonce']:
              # se lo è setto l'utente a None
              user = None
      #se non riesco ritorno None
      except:
          user = None
      # ritorno l'utente
      return user

  #metodo che salva in password l'hash della password passata
  def hash_password(self, password):
      self.validate_password("password", password)
      self.password = pwd_context.encrypt(password)

  #metodo che salva genera, hasha e salva un nuovo nonce di lunghezza ##length numeri consecutivi (in media di 2/3 cifre)
  def renew_nonce(self, length = 16):
      self.nonce = ''.join(str(x) for x in map(ord, os.urandom(length)))
  #metodo che salva genera, hasha e salva un nuovo change_password_nonce di lunghezza ##length numeri consecutivi (in media di 2/3 cifre)
  def renew_change_password_nonce(self, length = 16):
      self.change_password_nonce = ''.join(str(x) for x in map(ord, os.urandom(length)))

  #metodo che controlla se la password candidata è equivalente all'hash salvato
  def check_password(self, candidate):
      return pwd_context.verify(candidate, self.password)
