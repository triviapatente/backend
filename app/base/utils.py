from flask.json import JSONEncoder
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
