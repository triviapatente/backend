# -*- coding: utf-8 -*-

from flask import request

#chiave associata al token negli header http di ogni richiesta (il valore è deciso qui)
TOKEN_KEY = 'tp-session-token'
#chiamata che a partire da una richiesta ritorna il token.
#centralizzata, cosi la si può usare dappertutto
def tokenFromRequest():
    return request.headers.get(TOKEN_KEY)
