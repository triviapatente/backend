# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys

import eventlet

eventlet.monkey_patch()
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

print 'Running the service..'
debug = app.config["DEBUG"]
port = app.config["PORT"]
host = "0.0.0.0"
if debug == False:
    certfile = app.config["SSL_CERT_PATH"]
    keyfile = app.config["SSL_PRIVATE_KEY_PATH"]
    socketio.run(app, host = host, port = port, debug = debug, certfile = certfile, keyfile = keyfile)
else:
    socketio.run(app, host = host, port = port, debug = debug)



call(["fuser", "-k", "%d/tcp" % port])
