# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Float
from tp.base.models import *
#elemento che rappresenta un elemento disponibile nel negozio
class ShopItem(Base, CommonPK):
    #costo dell'elemento
    price = Column(Float, nullable = False)
    #nome dell'elemento
    name = Column(String, nullable = False)
    #emoji associata
    emoji = Column(String, nullable = False)
