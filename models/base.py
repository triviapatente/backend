# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime

import pytz

#la classe base è la classe su cui si appoggia ogni oggetto
class Base(object):
  	#ora non servirà più dichiarare __tablename__ in ogni classe
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
	#mysql default engine, permette di gestire le relazioni
    __table_args__ = {'mysql_engine': 'InnoDB'}

    #createdAt, parametro che indica la data di creazione, comune a tutti
    createdAt = Column(DateTime, default = datetime.now(pytz.utc))
    #updatedAt, parametro che indica la data di ultima modifica, comune a tutti
    updatedAt = Column(DateTime, default = datetime.now(pytz.utc))

Base = declarative_base(cls = Base)
