# -*- coding: utf-8 -*-

# file che contiene routines utili a livello globale

from app.exceptions import *
from app import db
from flask import g

# routine per le transazioni in db, riceve come parametro una funzione ##transaction che contiene le operazioni della transazione
# in ##params sono contenuti i parametri da passare alla funzione (sono un dizionario)
def doTransaction(transaction, **params):
    if not callable(transaction):
        raise ChangeFailed()
    # inizio la transazione
    # permetto più subtransactions nella stessa transazione (quindi è possibile chiamare più volte doTransaction in transaction)
    db.session.begin(subtransactions=True) #in teoria è di default perchè funziona comunque
    try:
        transaction(**params)
    except:
        # se avvengono errori torno indietro all'ultimo savepoint (o all'inizio se non ci sono)
        db.session.rollback()
    # per permettere il salvataggio in caso di savepoint il commit è fuori dal blocco try
    db.session.commit()

# routine per chiamare un savepoint nella transazione
def createSavePoint():
    db.session.begin_nested() # in caso di rollback mantiene i dati in stage (db.session.add(.))
