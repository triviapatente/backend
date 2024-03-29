# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Enum, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

import json

from tp import db, app

#la classe base è la classe su cui si appoggia ogni oggetto
class Base(db.Model):

    #è una classe astratta quindi lo indichiamo
    __abstract__ = True

    def __getitem__(self, key):
        if isinstance(key, str):
            return getattr(self, key)
        return None

    def __setitem__(self, key, value):
        if isinstance(key, str):
            setattr(self, key, value)

    export_properties = []
  	#ora non servirà più dichiarare __tablename__ in ogni classe
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    #createdAt, parametro che indica la data di creazione, comune a tutti
    createdAt = Column(DateTime(timezone=True), default = db.func.current_timestamp())
    #updatedAt, parametro che indica la data di ultima modifica, comune a tutti
    updatedAt = Column(DateTime(timezone=True), default = db.func.current_timestamp(),
                                 onupdate = db.func.current_timestamp())

    #metodo che serializza l'oggetto in json
    @property
    def json(self):
        output = {}
        #ottengo le colonne/proprietà per l'export (tranne json)
        values = self.export_values()
        #per ognuna
        for value in values:
            if hasattr(self, value):
                output[value] = getattr(self, value)
        return output

    #metodo che ottiene i nomi di tutti i valori dell'oggetto che devono essere esportati all'esterno
    @classmethod
    def export_values(self):
        return self.properties(include_json = False) + self.columns() + self.export_properties
    #metodo che ottiene i nomi di tutte le proprietà dell'oggetto
    @classmethod
    def properties(self, include_json = True):
        output = []
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, property):
                if include_json or name != "json":
                    output.append(name)
        return output

    #metodo che ottiene il tipo di una proprietà a partire dalla stessa
    def column(key):
        return self.__table__.columns[key]
    @classmethod
    def columns(self):
        output = []
        for column in self.__table__.columns:
            output.append(column.name)
        return output

#la classe commonpk è derivata da ogni classe che ha bisogno di id come chiave primaria
class CommonPK(db.Model):

    #è una classe astratta quindi lo indichiamo
    __abstract__ = True

    #questo è l'id, l'elemento che hanno in comune
    id =  Column(BigInteger, primary_key = True)

MAX_FEEDBACK_CHARS_FOR_FIELD = app.config["MAX_FEEDBACK_CHARS_FOR_FIELD"]
#la classe feedback è usata per immagazzinare i feedback degli utenti
class Feedback(Base, CommonPK):
    #contenuto del messaggio, TODO: controllare se funzionano le emoji
    message = Column(String(MAX_FEEDBACK_CHARS_FOR_FIELD), nullable = False)
    #utente che ha inviato il messaggio (può essere null in caso di messaggi anonimi)
    user_id = Column(BigInteger, ForeignKey("user.id"))
    user = relationship("User")
    #gioco in cui è stato inviato il messaggio
    scope = Column(Enum("complaint", "hint", "other", name='feedback_type'), nullable = False)
