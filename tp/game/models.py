# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table, Boolean, UniqueConstraint, BigInteger
from sqlalchemy.orm import relationship
from flask import g
from tp.base.models import Base, CommonPK
from tp.auth.models import User
from tp import app

class Partecipation(Base):
    user_id = Column('user_id', Integer, ForeignKey('user.id'), primary_key = True)
    user = relationship("User", back_populates = "games")
    game_id = Column('game_id', Integer, ForeignKey('game.id'), primary_key = True)
    game = relationship("Game", back_populates = "users")
    score_increment = Column('score_increment', Integer, default = 0)

class Game(Base, CommonPK):
  #utenti che partecipano al gioco
  users = relationship("Partecipation", back_populates = "game")
  #utente vincitore
  winner_id = Column(BigInteger, ForeignKey("user.id"))
  winner = relationship("User", foreign_keys = [winner_id])
  #the id of the player that invited other players to this game at the beginning
  creator_id = Column(BigInteger, ForeignKey("user.id"))
  creator = relationship("User", foreign_keys = [creator_id])
  #il gioco è finito?
  ended = Column(Boolean, default = False)

  export_properties = ["my_turn", "opponent_id", "opponent_username", "opponent_image", "question"]
  #ottiene l'utente avversario all'utente userToExclude e lo inserisce nel modello per la serializzazione
  def getOpponentForExport(self, userToExclude = None):
      #ho fatto il controllo qui e non direttamente nell'intestazione del metodo perchè i valori di default vengono interpretati a livello di bootstrap, e quindi g sarebbe fuori dall'application/request context
      if not userToExclude:
          userToExclude = g.user
      opponent = User.query.join(Partecipation).filter(Partecipation.game_id == self.id).filter(Partecipation.user_id != userToExclude.id).first()
      #DEVE esserci, ma controllo lo stesso per sicurezza
      if opponent:
          self.opponent_id = opponent.id
          self.opponent_image = opponent.image
          self.opponent_username = opponent.username


#rappresenta il round di un game, con categoria che ha scelto, game di appartenenza, domande proposte
class Round(Base, CommonPK):
  #numero del round, TODO: trovare il modo di farlo diventare autoincrement rispetto a diversi parametri
  number = Column(Integer, nullable = False)
  #match di riferimento
  game_id = Column(BigInteger, ForeignKey("game.id"), nullable = False)
  game = relationship("Game")
  #rappresenta il dealer del round, ovvero chi sceglie le categorie!
  dealer_id = Column(BigInteger, ForeignKey("user.id"), nullable = False)
  dealer = relationship("User")
  #categoria scelta per il round
  cat_id = Column(BigInteger, ForeignKey("category.id"))
  chosen_category = relationship("Category")

  __table_args__ = (UniqueConstraint('game_id', 'number', name = "unique_game_number"), )

class Quiz(Base, CommonPK):
  #la domanda del quiz, in lettere
  question = Column(String, nullable = False)
  #la risposta giusta, Vero/Falso
  answer = Column(Boolean, nullable = False)
  #l'immagine di riferimento, se presente
  image_id = Column(BigInteger, ForeignKey("image.id"))
  image = relationship("Image")
	#la categoria di riferimento (si punta sul fatto che ogni quiz sia categorizzato)
  category_id = Column(BigInteger, ForeignKey("category.id"), nullable = False)
  category = relationship("Category")

  export_properties = ["answered_correctly", "my_answer"]



class Question(Base):
  #quiz estratto
  quiz_id = Column(BigInteger, ForeignKey("quiz.id"), nullable = False, primary_key = True)
  quiz = relationship("Quiz")
  #risposta data dall'utente
  answer = Column(Boolean, nullable = False)

  round_id = Column(BigInteger, ForeignKey("round.id"), nullable = False, primary_key = True)
  user_id = Column(BigInteger, ForeignKey("user.id"), nullable = False, primary_key = True)
  export_properties = ["round_number"]

class Invite(Base):
    #il game a cui sei stato invitato
    game_id = Column(BigInteger, ForeignKey("game.id"), nullable = False, primary_key = True)
    game = relationship("Game")
    #chi ha invitato
    sender_id = Column(BigInteger, ForeignKey("user.id"), nullable = False, primary_key = True)
    sender = relationship("User", foreign_keys = [sender_id])
    #chi ha ricevuto l'invito
    receiver_id = Column(BigInteger, ForeignKey("user.id"), nullable = False, primary_key = True)
    receiver = relationship("User", foreign_keys = [receiver_id])
    #l'invito è stato accettato? NB: questo valore ragiona a logica ternaria (True|False|NULL), in quanto un invito potrebbe non essere ne stato accettato ne rifiutato, e quindi il valore diventa NULL
    accepted = Column(Boolean, nullable = True, default = None)

class Image(Base, CommonPK):
  #path dell'immagine, in alternativa: blob
  image = Column(String)

  @property
  def imagePath(self):
      return "../" + self.image

class Category(Base, CommonPK):
  #nome della categoria
  name = Column(String, nullable = False)
  #hint della categoria
  hint = Column(String)
  #colore della categoria
  color = Column(String)

  @property
  def imagePath(self):
    folder = app.config["CATEGORY_IMAGE_FOLDER"]
    return "../%s%d.png" % (folder, self.id)

#categoria proposta al giocatore, che deve sceglierla
class ProposedCategory(Base):
  #categoria proposta
  category_id = Column(BigInteger, ForeignKey("category.id"), nullable = False, primary_key = True)
  #turno in cui è stata proposta
  round_id = Column(BigInteger, ForeignKey("round.id"), nullable = False, primary_key = True)

#domande proposte al giocatore per un turno specifico
class ProposedQuestion(Base):
  #categoria proposta
  quiz_id = Column(BigInteger, ForeignKey("quiz.id"), nullable = False, primary_key = True)
  #turno in cui è stata proposta
  round_id = Column(BigInteger, ForeignKey("round.id"), nullable = False, primary_key = True)
