# -*- coding: utf-8 -*-
from flask.json import JSONEncoder
from flask import g

#classe che viene utilizzata internamente da flask per fare il JSON encoding di una classe
class TPJSONEncoder(JSONEncoder):
    def default(self, obj):
        #la classe ha la proprietà json? (Base e le sue derivate la hanno)
        serialized = getattr(obj, "json", None)
        if serialized:
            #se si, ritornala direttamente
            return serialized
        #se no, gestisci con la classe padre (genererà un errore se la classe non è serializable)
        return super(TPJSONEncoder, self).default(obj)


#metodo che a partire da un id di room e di un tipo di room, ne costruisce il nome
def roomName(id, type):
    return "%s_%s" % (type, id)
