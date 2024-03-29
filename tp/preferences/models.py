# -*- coding: utf-8 -*-

from tp.base.models import *
from sqlalchemy import Column, Integer, ForeignKey, Boolean, Enum, BigInteger
from sqlalchemy.orm import relationship

class Preferences(Base, CommonPK):
    #mostra le statistiche dell'utente a tutti, solo agli amici o a nessuno
    stats = Column(Enum("all", "friends", "nobody", name = "stats_preferences"), default = "all")
    #l'utente vuole ricevere messaggi da tutti, solo dagli amici o da nessuno
    chat = Column(Enum("all", "friends", "nobody", name = "chat_preferences"), default = "all")
    #notifiche
    notification_round = Column(Boolean, nullable = False, default = True)
    notification_new_game = Column(Boolean, nullable = False, default = True)
    notification_message = Column(Boolean, nullable = False, default = True)
    notification_full_hearts = Column(Boolean, nullable = False, default = True)
    #user
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable = False)
    user = relationship("User")
