# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.base.models import Base, CommonPK

class Message(Base, CommonPK):
  #contenuto del messaggio, TODO: controllare se funzionano le emoji
  content = Column(String, nullable = False)
  #utente che ha inviato il messaggio
  user_id = Column(Integer, ForeignKey("user.id"), nullable = False)
  user = relationship("User")
  #gioco in cui è stato inviato il messaggio
  game_id = Column(Integer, ForeignKey("game.id"), nullable = False)
  game = relationship("Game")
