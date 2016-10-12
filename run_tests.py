# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import sys

    reload(sys)
    sys.setdefaultencoding('utf8')
    #importo il progetto e la inizializzo
    import tp
    tp.init(True, need_ci)
    
    import unittest

    #creiamo le tabelle necessarie al testing
    from subprocess import call
    call(["sudo", "sh", "scripts/init_test.sh"])
    #controllo se si tratta di gitlab:ci
    need_ci = len(sys.argv) >= 2 and sys.argv[1] == "-ci"
    #elimino eventuali parametri aggiuntivi se presenti
    sys.argv = sys.argv[:1]


    #importo l'app
    from tp import app
    #importo i test
    from test.pipeline import *
    app.config['TESTING'] = True
    unittest.main()
    app.config['TESTING'] = False
