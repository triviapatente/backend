# -*- coding: utf-8 -*-

# file che contiene routines utili a livello globale

from app.exceptions import *
from app import db
from flask import g, request
from app.auth.models import *
from app.base.models import *
from app.game.models import *
from app.preferences.models import *
import traceback
# routine per le transazioni in db, riceve come parametro una funzione ##transaction che contiene le operazioni della transazione
# in ##params sono contenuti i parametri da passare alla funzione (sono un dizionario)
def doTransaction(transaction, **params):
    # controllo che transaction sia una funzione
    if not callable(transaction):
        print "The transaction you passed is not callable"
        return False
    # inizio la transazione
    # permetto più subtransactions nella stessa transazione (quindi è possibile chiamare più volte doTransaction in transaction)
    db.session.begin(subtransactions=True)
    try:
        output = transaction(**params)
    except Exception as e:
        print "Error while executing transaction: %s", str(e)
        print traceback.format_exc()
        # se avvengono errori torno indietro all'ultimo savepoint (o all'inizio se non ci sono)
        db.session.rollback()
        return False #se la funzione non ritorna niente non è andata a buon fine
    # per permettere il salvataggio in caso di savepoint il commit è fuori dal blocco try
    db.session.commit()
    db.session.commit() # non si sa perchè ne servano due in caso di flush
    if output:
        return output # permetto di ricevere il return se questo è presente
    return True

# routine per chiamare un savepoint nella transazione
def createSavePoint():
    db.session.begin_nested() # in caso di rollback mantiene i dati in stage (db.session.add(.))

#metodo che a partire da un tipo di richiesta ritorna il tipo di store da cui andare a prenderne i parametri
def storeForMethod(method):
    if method == "POST":
        return request.form
    elif method == "FILE":
        return request.files
    elif method == "SOCKET":
        return request.event["args"][0]
    return None

#metodo che a partire da un tipo di richiesta ritorna il nome della chiave in cui andare a mettere i parametri una volta presi dal decorator, dentro g
def outputKeyForMethod(method):
    if method == "POST":
        return "post"
    elif method == "FILE":
        return "files"
    elif method == "SOCKET":
        return "params"
    return None
