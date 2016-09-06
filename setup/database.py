# -*- coding: utf-8 -*-


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

from models import category, game, installation, Keychain, Message, Partecipation, Quiz, Round, User
from models.base import Base
def initialize():
	engine = create_engine("sqlite:///restaurantmenu.db")
	Base.metadata.create_all(engine)
