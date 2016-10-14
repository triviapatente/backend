# -*- coding: utf-8 -*-

from api import *
from test.shared import TPAuthTestCase
from tp.purchases.models import ShopItem
# poi servirà l'autenticazione
class PurchasesHTTPTestCase(TPAuthTestCase):
    def setUp(self):
        super(PurchasesHTTPTestCase, self).setUp()
        ShopItem.init()
    ###TEST METHODS###
    #per creare un metodo di test basta mettere test_ prima del metodo
    def test_getItems(self):
        response = getItems(self)

        print "#1 All items received correctly"
        assert response.json.get("items")

        # altri test implementerebbero il metodo da testare stesso
