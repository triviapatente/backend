# -*- coding: utf-8 -*-

#file che contiene i diversi tipi di eccezione usati all'interno dell'api
#eccezione generica, che definisce il modo di serializzare in dizionario l'eccezione
class TPException(Exception):
    status_code = 400 #bad request
    message = ""
    parameters = None
    payload = {}
    def __init__(self):
        Exception.__init__(self)

    def to_dict(self):
        rv = dict()
        rv['message'] = self.message
        rv['parameters'] = self.parameters
        rv['success'] = False
        rv["status_code"] = self.status_code
        rv = {k: v for k, v in rv.items() if v != None}
        return rv
class AlreadyPendingGame(TPException):
    status_code = 403 #unauthorized

    def __init__(self):
        TPException.__init__(self)
        self.message = "Hai già un match da iniziare con questo utente!"
#eccezione chiamata quando un parametro richiesto è mancante
class MissingParameter(TPException):
    status_code = 400 #bad request

    def __init__(self, parameters):
        TPException.__init__(self)
        self.message = "Alcuni parametri della richiesta non sono presenti"
        self.parameters = parameters

#eccezione chiamata quando un parametro richiesto ha un formato/valore errato
class BadParameters(TPException):
    status_code = 400 #bad request

    def __init__(self, parameters, message = None):
        TPException.__init__(self)
        if message:
            self.message = message
        else:
            self.message = "Alcuni parametri della richiesta sono errati"
        self.parameters = parameters

#eccezione chiamata quando un parametro richiesto eccede il massimo numero di caratteri
class MaxCharacters(TPException):
    status_code = 400 #bad request

    def __init__(self, parameters, message = None):
        TPException.__init__(self)
        if message:
            self.message = message
        else:
            self.message = "Massimo numero di caratteri raggiunto."
        self.parameters = parameters

#eccezione chiamata quando l'utente da inserire è già esistente
class AlreadyRegisteredUser(TPException):
    status_code = 403 #unauthorized

    def __init__(self, previousUser, username, email):
        TPException.__init__(self)
        self.message = "Esiste già un utente con questo"
        duplicateUsername = (username == previousUser.username)
        duplicateEmail = (email == previousUser.email)
        if duplicateUsername and duplicateEmail:
            self.message = self.message + " username e questa email: {0}, {1}".format(username, email)
        elif duplicateEmail:
            self.message = self.message + " indirizzo email: {0}".format(email)
        elif duplicateUsername:
            self.message = self.message + " username: {0}".format(username)

class NotFound(TPException):
    status_code = 404
    def __init__(self):
        TPException.__init__(self)
        self.message = "L'elemento non è stato trovato"

#eccezione chiamata quando il login dell'utente fallisce
class LoginFailed(TPException):
    status_code = 400

    def __init__(self):
        TPException.__init__(self)
        self.message = "Associazione username (o email) e password errata. Riprova!"

#eccezione chiamata quando il login dell'utente fallisce
class Forbidden(TPException):
    status_code = 401

    def __init__(self):
        TPException.__init__(self)
        self.message = "Autenticazione richiesta, rieffettua il login"

class ChangeFailed(TPException):
    status_code = 500 #Internal Server Error

    def __init__(self):
        TPException.__init__(self)
        self.message = "Modifica non effettuata"

class FormatNotAllowed(TPException):
    status_code = 405 #Method not allowed

    def __init__(self):
        TPException.__init__(self)
        self.message = "Il file ha un' estensione non permessa dai nostri server"
class NotAllowed(TPException):
    status_code = 403 #not allowed

    def __init__(self):
        TPException.__init__(self)
        self.message = "Non hai i permessi di accesso su questa risorsa"

class OldPasswordNotMatching(TPException):
    status_code = 403

    def __init__(self):
        TPException.__init__(self)
        self.message = "Modifica non consentita: la password attualmente impostata non combacia con quella fornita"

class FBTokenNotValidException(TPException):
    status_code = 403

    def __init__(self):
        TPException.__init__(self)
        self.message = "L'autorizzazione con Facebook non è andata a buon fine. Riprova!"
