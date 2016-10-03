# -*- coding: utf-8 -*-
from datetime import datetime
from app import db
#metodo che ritorna un array che contiene tutti i modelli che sqlalchemy gestisce
def getDBModels():
    return db.metadata.tables.items()

#metodo che ritorna un dictionary che contiene un oggetto per ogni modello presente in db, popolato con valori arbitrari
def getJSONModels():
    models = getDBModels()
    output = {}
    for name, table in models:
        item = {}
        for column in table.columns:
            item[column.name] = getDefaultValueForType(column.type)
        output[name] = item
    return output

from sqlalchemy import String, Integer, DateTime, Boolean, Enum
#metodo che a partire da un tipo di sqlalchemy ritorna un valore a caso di quel tipo che possa far capire a livello di json di cosa stiamo parlando
def getDefaultValueForType(candidate):
    #devo usare due array paralleli perchè python non supporta le map con valori non hashabili come chiavi
    types = [String, Integer, DateTime, Boolean, Enum]
    values = ["stringa", 22, datetime.today().isoformat(), True, "enum_value"]

    for i, type in enumerate(types):
        if str(candidate) == str(type()):
            return values[i]
    return None
