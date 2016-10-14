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

    #metodo che inizializza gli elementi dello shop nel db
    @staticmethod
    def init():
        ShopItem.query.delete()
        item1 = ShopItem(id = 1, price = 9.99, name = "Vite infinite", emoji = "😍")
        item2 = ShopItem(id = 2, price = 5.99, name = "100 vite", emoji = "💖")
        item3 = ShopItem(id = 3, price = 4.99, name = "75 vite", emoji = "💘")
        item4 = ShopItem(id = 4, price = 2.99, name = "50 vite", emoji = "💝")
        item5 = ShopItem(id = 5, price = 1.99, name = "25 vite", emoji = "💕")
        item6 = ShopItem(id = 6, price = 0.49, name = "5 vite", emoji = "❤️")
        db.session.add_all([item1, item2, item3, item4, item5, item6])
        db.session.commit()
