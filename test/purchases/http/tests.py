# -*- coding: utf-8 -*-

from test.purchases.http.api import *
from test.shared import TPAuthTestCase
from tp.purchases.models import ShopItem
# poi servirà l'autenticazione
class PurchasesHTTPTestCase(TPAuthTestCase):
    def setUp(self):
        super(PurchasesHTTPTestCase, self).setUp()
        ShopItem.init()

    def test_getItems(self):
        response = getItems(self)
        print("#1 All items received correctly")
        assert response.json.get("items")
