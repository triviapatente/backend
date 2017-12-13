# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from tp.base.models import Base, CommonPK
from tp.game.models import Game
from tp.auth.models import User


class Installation(Base, CommonPK):
    #sistema operativo del device in cui è installata la app
    os = Column(Enum("iOS", "Android", name = "os_type_enum"), nullable = False)
    #token che rappresenta l'installazione in uno specifico device dell'app
    token = Column(String, nullable = False)
    #id che rappresenta univocamente un device
    device_id = Column(String, nullable = False)
    #utente associato a questa installazione
    user_id = Column(Integer, ForeignKey("user.id"), nullable = False)
    user = relationship(User)

class Socket(Base):
    #utente collegato
    user_id = Column(Integer, ForeignKey("user.id"), nullable = False)
    user = relationship(User)
    #socket id della connessione
    socket_id = Column(String, primary_key = True, nullable = False)

class RoomParticipation(Base):
    #utente collegato
    game_id = Column(Integer, ForeignKey("game.id"), primary_key = True, nullable = False)
    game = relationship(Game)
    #socket id della connessione
    socket_id = Column(String, ForeignKey("socket.socket_id"), primary_key = True, nullable = False)
