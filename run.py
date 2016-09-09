# -*- coding: utf-8 -*-
#!/usr/bin/python

import sys

#se lo script non è stato chiamato con la flag che forza l'avvio impedendo l'inizializzazione
if len(sys.argv) < 2 or sys.argv[1] != "--f":
    #esegui lo script di inizializzazione dell'app (che installa anche le dipendenze)
    from subprocess import call
    call(["sudo", "sh", "dependencies.sh"])

from app import app

app.run(host = '0.0.0.0', port = 8080, debug = app.config["DEBUG"])
