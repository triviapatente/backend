# -*- coding: utf-8 -*-

#file che contiene i diversi tipi di eccezione usati all'interno dell'api
#eccezione generica, che definisce il modo di serializzare in dizionario l'eccezione
class TPException(Exception):
    status_code = 404
    message = ""
    parameters = None
    payload = {}
    def __init__(self):
        Exception.__init__(self)

    def to_dict(self):
        rv = dict()
        rv['message'] = self.message
        rv['parameters'] = self.parameters
        rv = {k: v for k, v in rv.items() if v}
        return rv

#eccezione chiamata quando un parametro richiesto è mancante
class MissingParameter(TPException):
    status_code = 404

    def __init__(self, parameters):
        TPException.__init__(self)
        self.message = "Alcuni parametri della richiesta non sono presenti"
        self.parameters = parameters

#eccezione chiamata quando l'utente da inserire è già esistente
class AlreadyRegisteredUser(TPException):
    status_code = 404
    def __init__(self, previousUser, username, email):
        TPException.__init__(self)
        self.message = "Esiste già un utente con questo "
        if username == previousUser.username:
            self.message = self.message + "username: {0}".format(username)
        elif email == previousUser.email:
            self.message = self.message + "indirizzo email: {0}".format(email)
