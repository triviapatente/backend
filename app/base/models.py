from app.db import Column, DateTime, Model, Integer
import pytz

#la classe base è la classe su cui si appoggia ogni oggetto
class Base(Model):

    #è una classe astratta quindi lo indichiamo
    __abstract__ = True

  	#ora non servirà più dichiarare __tablename__ in ogni classe
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
	#mysql default engine, permette di gestire le relazioni
    __table_args__ = {'mysql_engine': 'InnoDB'}

    #createdAt, parametro che indica la data di creazione, comune a tutti
    createdAt = Column(DateTime, default = db.func.current_timestamp(),
                                 onupdate = db.func.current_timestamp())
    #updatedAt, parametro che indica la data di ultima modifica, comune a tutti
    updatedAt = Column(DateTime, default = db.func.current_timestamp())

#la classe commonpk è derivata da ogni classe che ha bisogno di id come chiave primaria
class CommonPK(Model):

    #è una classe astratta quindi lo indichiamo
    __abstract__ = True

    #questo è l'id, l'elemento che hanno in comune
    id =  Column(Integer, primary_key = True)
