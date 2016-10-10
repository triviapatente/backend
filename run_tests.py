import sys

reload(sys)
sys.setdefaultencoding('utf8')

import unittest

#importo i test
from test.pipeline import *


if __name__ == '__main__':
    unittest.main()
