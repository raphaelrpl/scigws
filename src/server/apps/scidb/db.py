from exception import SciDBException, SciDBConnectionError

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

    def __del__(self):
        super(SciDB, self).__del__()

    def disconnect(self):
        try:
            super(SciDB, self).disconnect()
        except ValueError as e:
            raise SciDBException(e.message)

    def prepareQuery(self, query, lang="AFL"):
        return super(SciDB, self).preparyQuery(query, lang)

    def executeQuery(self, query, lang="AFL"):
        if not self._handle:
            raise SciDBConnectionError("no open connection")
        try:
            db = scidbapi.swig.getSciDB()
            if lang in ("afl", "AFL"):
                type_num = scidbapi.swig.AFL
            elif lang in ("aql", "AQL"):
                type_num = scidbapi.swig.AQL
            else:
                raise SciDBException("Type must be 'afl' or 'aql', it was %s for query %s" % (lang, query))
            result = scidbapi.swig.QueryResult()
            db.executeQuery(query, type_num, result, self._handle)  # or take a prepared query
            return result
        except Exception, inst:
            print >> sys.stderr, "Exception of type %s value %s" % (Exception, inst,)
            print >> sys.stderr, "re-raising ...."
            raise
        # return super(SciDB, self).executeQuery(query, lang)

    def cancelQuery(self, query_id):
        """ Cancel SciDB query and return status code """
        return super(SciDB, self).cancelQuery(query_id)

    def completeQuery(self, query_id):
        """ Complete SciDB query and return status code """
        return super(SciDB, self).completeQuery(query_id)


class QueryResult(scidbapi.swig.QueryResult):
    def __init__(self):
        super(QueryResult, self).__init__()


attribute_type_string_funcs = {
    "char": scidbapi.swig.Value.getChar,
    "string": scidbapi.swig.Value.getString,
    "datetime": scidbapi.swig.Value.getDateTime,
    "indicator": lambda(x): True,
    "bool": scidbapi.swig.Value.getBool,
    "uint8": scidbapi.swig.Value.getUint8,
    "uint16": scidbapi.swig.Value.getUint16,
    "uint32": scidbapi.swig.Value.getUint32,
    "uint64": scidbapi.swig.Value.getUint64,
    "int8": scidbapi.swig.Value.getInt8,
    "int16": scidbapi.swig.Value.getInt16,
    "int32": scidbapi.swig.Value.getInt32,
    "int64": scidbapi.swig.Value.getInt64,
    "float": scidbapi.swig.Value.getFloat,
    "double": scidbapi.swig.Value.getDouble,
}