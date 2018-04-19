# -*- coding: utf-8 -*-

if __name__ == '__main__':

    import eventlet

    eventlet.monkey_patch()
    import sys

    reload(sys)
    sys.setdefaultencoding('utf8')
    #importo il progetto e la inizializzo
    import tp
    #controllo se si tratta di gitlab:ci
    need_ci = len(sys.argv) >= 2 and sys.argv[1] == "-ci"
    tp.init(True, need_ci)

    import unittest
    #elimino il parametro -ci, perchè unittest esamina i parametri in cerca di testcase singoli
    if need_ci:
        try:
            i = sys.argv.index("-ci")
            del sys.argv[i]
        except ValueError:
            pass


    #importo l'app
    from tp import app
    #importo i test
    from test.pipeline import *
    app.config['TESTING'] = True
    unittest.main()
    app.config['TESTING'] = False
