# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys

reload(sys)
sys.setdefaultencoding('utf8')

from subprocess import call

#se lo script non è stato chiamato con la flag che forza l'avvio impedendo l'inizializzazione
if len(sys.argv) >= 2 and sys.argv[1] == "-update":
    #esegui lo script di inizializzazione dell'app (che installa anche le dipendenze)
    call(["sudo", "sh", "scripts/dependencies.sh"])


import tp
tp.init()

from tp import app, socketio

debug = app.config["DEBUG"]
port = app.config["PORT"]
context = None
if debug == False:
    context = (app.config["SSL_CERT_PATH"], app.config["SSL_PRIVATE_KEY_PATH"])

print 'Running the service..'
socketio.run(app, host = '0.0.0.0', port = port, debug = debug, ssl_context=context)

call(["fuser", "-k", "%d/tcp" % port])
