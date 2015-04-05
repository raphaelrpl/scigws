from exception import SciDBConnectionError
from server.settings import SCIDB_VERSION

import os
import sys

sys.path.append(os.path.join('/opt/scidb/%s' % SCIDB_VERSION, 'lib'))
import scidbapi


class SciDB(scidbapi.Connection):
    def __init__(self, host, port=1239):
        try:
            db = scidbapi.swig.getSciDB()
            handle = db.connect(str(host), port=int(port))
            super(SciDB, self).__init__(handle)
        except Exception as error:
            raise SciDBConnectionError(error)