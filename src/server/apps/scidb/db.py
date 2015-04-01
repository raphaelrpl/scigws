from exception import SciDBConnectionError

import os
import sys

sys.path.append(os.path.join('/opt/scidb/14.3', 'lib'))
import scidbapi


class SciDB(scidbapi.Connection):
    def __init__(self, host, port=1239):
        try:
            db = scidbapi.swig.getSciDB()
            handle = db.connect(host, port=int(port))
            super(SciDB, self).__init__(handle)
        except Exception as error:
            raise SciDBConnectionError(error)