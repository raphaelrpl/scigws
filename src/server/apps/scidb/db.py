from exception import SciDBConnectionError
from server.settings import SCIDB_VERSION

import os
import sys
import numpy as np

sys.path.append(os.path.join('/opt/scidb/%s' % SCIDB_VERSION, 'lib'))
import scidbapi


class SciDBResultSet:
    query_result = None
    attr_iterators = None
    chunk_iterators = None

    def __init__(self, query_result):
        self.query_result = query_result
        desc = self.query_result.array.getArrayDesc()
        self.attr_iterators = [
            (attr, self.query_result.array.getConstIterator(attr.getId())) for attr in desc.getAttributes()
            if attr.getName() != "EmptyTag"
        ]

        self.__update()

    def __iter__(self):
        return self

    def next(self):
        """return the next row of data if it is available otherwise raise StopIteration"""

        chunk_iter = self.chunk_iterators[0][1]

        if chunk_iter.end():
            # increment each attribute iterator to the next chunk
            for iterator in self.attr_iterators:
                iterator[1].increment_to_next()

            # attempt to update the chunk iterators based on the incremented
            # attribute iterators
            if self.__update():
                raise StopIteration

        # get dimension values at this position
        coordinates = self.chunk_iterators[0][1].getPosition()  # get the first tuple from the list,
        # then get the second item in the tuple
        pos_list = []
        for i in range(len(coordinates)):
            pos_list.append(coordinates[i])

        # get attribute values at this position
        attr_values = []
        for chunk_iterator in self.chunk_iterators:
            attr = chunk_iterator[0]
            chunk_iter = chunk_iterator[1]

            if not chunk_iter.isEmpty():
                attr_values.append(scidbapi.getTypedValue(chunk_iter.getItem(), attr.getType()))
            else:
                attr_values.append(None)

            chunk_iter.increment_to_next()

        return pos_list, attr_values

    def __update(self):
        """return True if the end has been reached otherwise return False"""
        self.chunk_iterators = []

        end = self.attr_iterators[0][1].end()

        if not end:
            for attr_iter_tuple in self.attr_iterators:
                attr = attr_iter_tuple[0]
                attr_iter = attr_iter_tuple[1]

                current_chunk = attr_iter.getChunk()
                chunk_iter = current_chunk.getConstIterator(
                    scidbapi.swig.ConstChunkIterator.IGNORE_OVERLAPS |
                    scidbapi.swig.ConstChunkIterator.IGNORE_EMPTY_CELLS
                )
                self.chunk_iterators.append((attr, chunk_iter))

        return end

    def to_array(self):
        values = [element[1] for element in self]
        return np.array(values)


class SciDB(scidbapi.Connection):
    objects = None

    def __init__(self, host, port=1239):
        try:
            db = scidbapi.swig.getSciDB()
            handle = db.connect(str(host), port=int(port))
            super(SciDB, self).__init__(handle)
        except Exception as error:
            raise SciDBConnectionError(error)

    def executeQuery(self, query, lang="afl"):
        result = super(SciDB, self).executeQuery(query, lang)
        self.objects = SciDBResultSet(result)
        return result

    def __del__(self):
        if self.objects:
            print("Closing Active Query - ", self.objects.query_result.queryID)
            self.completeQuery(self.objects.query_result.queryID)