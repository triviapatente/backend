# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from tp import app, db
from tp.purchases.models import *

shop = Blueprint("shop", __name__, url_prefix = "/shop")

@shop.route("/", methods = ["GET"])
def welcome():
    output = app.config["PUBLIC_INFOS"]
    return jsonify(output)

@shop.route("/list", methods = ["GET"])
def getItems():
    output = ShopItem.query.all()
    return jsonify(items = output)

#metodo che inizializza i prezzi nel db
def initPrices():
    ShopItem.query.delete()
    item1 = ShopItem(id = 1, price = 9.99, name = "Vite infinite", emoji = "😍")
    item2 = ShopItem(id = 2, price = 5.99, name = "100 vite", emoji = "💖")
    item3 = ShopItem(id = 3, price = 4.99, name = "75 vite", emoji = "💘")
    item4 = ShopItem(id = 4, price = 2.99, name = "50 vite", emoji = "💝")
    item5 = ShopItem(id = 5, price = 1.99, name = "25 vite", emoji = "💕")
    item6 = ShopItem(id = 6, price = 0.49, name = "5 vite", emoji = "❤️")
    db.session.add_all([item1, item2, item3, item4, item5, item6])
    db.session.commit()
