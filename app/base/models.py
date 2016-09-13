# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr

import json

from app import db

#la classe base è la classe su cui si appoggia ogni oggetto
class Base(db.Model):

    #è una classe astratta quindi lo indichiamo
    __abstract__ = True

  	#ora non servirà più dichiarare __tablename__ in ogni classe
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    #createdAt, parametro che indica la data di creazione, comune a tutti
    createdAt = Column(DateTime, default = db.func.current_timestamp())
    #updatedAt, parametro che indica la data di ultima modifica, comune a tutti
    updatedAt = Column(DateTime, default = db.func.current_timestamp(),
                                 onupdate = db.func.current_timestamp())


    #metodo che serializza l'oggetto in json
    @property
    def json(self):
        output = {}
        #ottengo le colonne generiche
        columns = self.columns()
        #per ognuna
        for column in columns:
            #vedo se ho la colonna scelta (potrei non averla, in caso di proprietà non settata)
            if self.hasProperty(column):
                #se la ho, me la prendo in output
                output[column] = self.get(column)
        return output

    #metodo che ritorna la proprietà dell'oggetto corrispondente alla chiave passata per parametro
    def get(self, key):
        return self.__dict__[key]

    #metodo che indica se l'oggetto contiene la proprietà key
    #esempio:
    # Classe A, 3 proprietà: one, two, three
    #a  = A(one = 1, three = 3)
    #a.hasProperty("one") #true
    #a.hasProperty("two") #false
    #a.hasProperty("three") #true

    def hasProperty(self, key):
        return self.__dict__.has_key(key)

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
    id =  Column(Integer, primary_key = True)
