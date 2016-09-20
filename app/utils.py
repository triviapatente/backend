# -*- coding: utf-8 -*-

# file che contiene routines utili a livello globale

from app.exceptions import *
from app import db
from flask import g
from app.auth.models import *
from app.base.models import *
from app.game.models import *
from app.preferences.models import *

# routine per le transazioni in db, riceve come parametro una funzione ##transaction che contiene le operazioni della transazione
# in ##params sono contenuti i parametri da passare alla funzione (sono un dizionario)
def doTransaction(transaction, **params):
    # controllo che transaction sia una funzione
    if not callable(transaction):
        raise ChangeFailed()
    # inizio la transazione
    # permetto più subtransactions nella stessa transazione (quindi è possibile chiamare più volte doTransaction in transaction)
    db.session.begin(subtransactions=True)
    # TODO permettere l'autoflush, quindi si può accedere ad esempio al campo id di un nuovo record (non ho trovato come fare)
    try:
        output = transaction(**params)
    except:
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
