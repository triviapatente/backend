# -*- coding: utf-8 -*-

import sys
#se lo script non è stato chiamato con la flag che forza l'avvio impedendo l'inizializzazione
if len(sys.argv) < 2 or sys.argv[1] != "--f":
    # installo le dipendenze
    from subprocess import call
    call(["sudo", "sh", "dependencies.sh"])
