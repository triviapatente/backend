# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table, Boolean
from sqlalchemy.orm import relationship

from app.base.models import Base, CommonPK


partecipation = Table('partecipation', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key = True),
    Column('game_id', Integer, ForeignKey('game.id'), primary_key = True)
)

class Game(Base, CommonPK):
  #utenti che partecipano al gioco
  users = relationship("User", secondary = partecipation, back_populates = "games")
  #utente vincitore
  winner_id = Column(Integer, ForeignKey("user.id"))
  winner = relationship("User", back_populates = "games_won")

#un round adesso rappresenta il round di un utente, e contiene tutte le info di quel round, come utente che sta giocando, categoria che ha scelto, game di appartenenza, domande proposte
class Round(Base):
  #numero del round, TODO: trovare il modo di farlo diventare autoincrement rispetto a diversi parametri
  number = Column(Integer, nullable = False)
  #match di riferimento
  game_id = Column(Integer, ForeignKey("game.id"), nullable = False, primary_key = True)
  game = relationship("Game")
  #utente che 'possiede' questo round
  user_id = Column(Integer, ForeignKey("user.id"), nullable = False, primary_key = True)
  user = relationship("User")
  #categoria scelta per il round
  cat_id = Column(Integer, ForeignKey("category.id"), nullable = False)
  chosen_category = relationship("Category")


class Quiz(Base, CommonPK):
  #la domanda del quiz, in lettere
  question = Column(String(250), nullable = False)
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
  #round di riferimento, espresso attraverso le sue due chiavi primarie, game_id, e user_id
  game_id = Column(Integer, ForeignKey("round.game_id"), nullable = False, primary_key = True)
  user_id = Column(Integer, ForeignKey("round.user_id"), nullable = False, primary_key = True)

class Image(Base, CommonPK):
  #path dell'immagine, in alternativa: blob
  image = Column(String)

class Category(Base, CommonPK):
  #nome della categoria
  name = Column(String(250), nullable = False)
