# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
from subprocess import call

#se lo script non è stato chiamato con la flag che forza l'avvio impedendo l'inizializzazione
if len(sys.argv) < 2 or sys.argv[1] != "--f":
    #esegui lo script di inizializzazione dell'app (che installa anche le dipendenze)
    call(["sudo", "sh", "scripts/dependencies.sh"])



from app import app, socketio

debug = app.config["DEBUG"]
port = app.config["PORT"]

print 'Running the service..'
socketio.run(app, host = '0.0.0.0', port = port, debug = debug)

call(["fuser", "-k", "%d/tcp" % port])
