# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from tp.base.models import Base, CommonPK

partecipation = Table('partecipation', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key = True),
    Column('game_id', Integer, ForeignKey('game.id'), primary_key = True)
)

class Game(Base, CommonPK):
  #utenti che partecipano al gioco
  users = relationship("User", secondary = partecipation, back_populates = "games")
  #utente vincitore
  winner_id = Column(Integer, ForeignKey("user.id"))
  winner = relationship("User", foreign_keys = [winner_id])
  #the id of the player that invited other players to this game at the beginning
  creator_id = Column(Integer, ForeignKey("user.id"))
  creator = relationship("User", foreign_keys = [creator_id])
  #il gioco è finito?
  ended = Column(Boolean, default = False)

#rappresenta il round di un game, con categoria che ha scelto, game di appartenenza, domande proposte
class Round(Base, CommonPK):
  #numero del round, TODO: trovare il modo di farlo diventare autoincrement rispetto a diversi parametri
  number = Column(Integer, nullable = False)
  #match di riferimento
  game_id = Column(Integer, ForeignKey("game.id"), nullable = False)
  game = relationship("Game")
  #rappresenta il dealer del round, ovvero chi sceglie le categorie!
  dealer_id = Column(Integer, ForeignKey("user.id"), nullable = False)
  dealer = relationship("User")
  #categoria scelta per il round
  cat_id = Column(Integer, ForeignKey("category.id"))
  chosen_category = relationship("Category")

  __table_args__ = (UniqueConstraint('game_id', 'number', name = "unique_game_number"), )

class Quiz(Base, CommonPK):
  #la domanda del quiz, in lettere
  question = Column(String, nullable = False)
  #la risposta giusta, Vero/Falso
  answer = Column(Boolean, nullable = False)
  #l'immagine di riferimento, se presente
  image_id = Column(Integer, ForeignKey("image.id"))
  image = relationship("Image")
	#la categoria di riferimento (si punta sul fatto che ogni quiz sia categorizzato)
  category_id = Column(Integer, ForeignKey("category.id"), nullable = False)
  category = relationship("Category")


class Question(Base):
  #quiz estratto
  quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable = False, primary_key = True)
  quiz = relationship("Quiz")
  #risposta data dall'utente
  answer = Column(Boolean, nullable = False)

  round_id = Column(Integer, ForeignKey("round.id"), nullable = False, primary_key = True)
  user_id = Column(Integer, ForeignKey("user.id"), nullable = False)

class Invite(Base):
    #il game a cui sei stato invitato
    game_id = Column(Integer, ForeignKey("game.id"), nullable = False, primary_key = True)
    game = relationship("Game")
    #chi ha invitato
    sender_id = Column(Integer, ForeignKey("user.id"), nullable = False, primary_key = True)
    sender = relationship("User", foreign_keys = [sender_id])
    #chi ha ricevuto l'invito
    receiver_id = Column(Integer, ForeignKey("user.id"), nullable = False, primary_key = True)
    receiver = relationship("User", foreign_keys = [receiver_id])
    #l'invito è stato accettato? NB: questo valore ragiona a logica ternaria (True|False|NULL), in quanto un invito potrebbe non essere ne stato accettato ne rifiutato, e quindi il valore diventa NULL
    accepted = Column(Boolean, nullable = True, default = None)

class Image(Base, CommonPK):
  #path dell'immagine, in alternativa: blob
  image = Column(String)

class Category(Base, CommonPK):
  #nome della categoria
  name = Column(String(250), nullable = False)
#categoria proposta al giocatore, che deve sceglierla
class ProposedCategory(Base):
  #categoria proposta
  category_id = Column(Integer, ForeignKey("category.id"), nullable = False, primary_key = True)
  #turno in cui è stata proposta
  round_id = Column(Integer, ForeignKey("round.id"), nullable = False, primary_key = True)

#domande proposte al giocatore per un turno specifico
class ProposedQuestion(Base):
  #categoria proposta
  quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable = False, primary_key = True)
  #turno in cui è stata proposta
  round_id = Column(Integer, ForeignKey("round.id"), nullable = False, primary_key = True)
