from django.core.exceptions import ObjectDoesNotExist
from apps.scidb.db import SciDB, scidbapi
from apps.scidb.exception import SciDBConnectionError
from exception import NoSuchCoverageException, InvalidSubset, InvalidAxisLabel, InvalidRangeSubSet, WCSException
from utils import WCS_MAKER
from validators import DateToPoint
from validators import is_valid_url
from apps.geo.models import GeoArrayTimeLine, GeoArray
from collections import defaultdict
from apps.ows.exception import MissingParameterValue, InvalidParameterValue

# Lib for parallel scidb data
from multiprocessing import Process, Queue

from threading import Thread

# numpy array
import numpy as np

from datetime import datetime


# Try import TerralibPy
try:
    import terralib
except ImportError:
    terralib = None


class WCS(object):
    geo_array = None
    data = {}
    bands = None
    attributes = None
    query = None

    def __init__(self, formats=[]):
        self.data = defaultdict(list)
        self.root_coverages_summary = WCS_MAKER("Contents")
        self.root_coverages_summary.extend([
            WCS_MAKER(
                "CoverageSummary",
                WCS_MAKER(
                    "CoverageId",
                    coverage.name
                ),
                WCS_MAKER(
                    "CoverageSubtype",
                    "GridCoverage"
                )
            )
            for coverage in GeoArray.objects.all()
        ])
        times = GeoArrayTimeLine.objects.all().order_by('id')

        self.times = defaultdict(list)
        for time in times:
            self.times[time.array].append(time)

    def get_coverages_summary(self):
        return self.root_coverages_summary

    def _get_subset_from(self, subset):
        params = {}
        for element in subset:
            try:
                args = filter(None, element.split('(')[1].strip(')').split(','))
            except IndexError:
                raise InvalidParameterValue("Invalid parameter \"%s\"" % element, locator="subset")
            if len(args) != 2:
                raise InvalidSubset(msg="Invalid subset \"%s\"" % element)
            sub = element.strip('').split('(')[0].split(',')
            key = sub[0]
            if key.lower() == "time_id":
                dimension = args
            else:
                dimension = map(int, args)
            if len(sub) > 1:
                epsg = sub[1].split('(')[0]
            else:
                epsg = ''
            if not is_valid_url(epsg):
                epsg = ''
            params[key] = {'epsg': epsg, 'dimension': dimension}
            if key != self.geo_array.x_dim_name and key != self.geo_array.y_dim_name \
                    and key != self.geo_array.t_dim_name:
                raise InvalidAxisLabel("\"%s\" is not valid axis. " % sub, locator="subset", version="2.0.1")
        return params

    def _get_bands_from(self, bands):
        if isinstance(bands, list):
            bands = bands[0]
        temp = filter(lambda b: b.replace(' ', ''), bands.split(','))
        geo_attr = self.geo_array.geoarrayattribute_set.filter(name__in=temp)
        if len(temp) == len(geo_attr):
            self.bands = temp
            return temp
        raise InvalidRangeSubSet(msg="Invalid rangesubset %s" % temp)

    def _parallel_getter_object(self, attribute, shared_object):
        # Define list of values retrieved
        array = []
        currentchunk = attribute[1].getChunk()
        chunkiter = currentchunk.getConstIterator(
            (
                scidbapi.swig.ConstChunkIterator.IGNORE_OVERLAPS) |
            (
                scidbapi.swig.ConstChunkIterator.IGNORE_EMPTY_CELLS))

        while not chunkiter.end():
            if not chunkiter.isEmpty():
                dataitem = chunkiter.getItem()
                array.append(scidbapi.getTypedValue(dataitem, attribute[2]))
            chunkiter.increment_to_next()

        # Putting array in queue (shared object - concurrency?)
        shared_object.put((attribute[0], array))

    # def _get_iterators_from_scidb(self, query, attrs, index, shared_object, shared_dtypes):
    def _get_iterators_from_scidb(self, query, attrs, index, shared_object):
        dtype = []
        name = attrs[index].getName()
        iterator = query.array.getConstIterator(index)
        print("Iterator -> {}".format(iterator))
        attribute_type = attrs[index].getType()
        attributes = (name, iterator, attribute_type)
        # shared_object.append(attributes)
        # shared_dtypes.append((name, attribute_type))
        shared_object.put((attributes, dtype))

    def get_scidb_data(self, statement, lang="afl"):
        """
        It retrieves SciDB Data using scidbapi interface. It stores a dict containing band and list of values

        :type statement: str
        :type lang: str
        :param statement: It is SciDB Query Statement
        :param lang: SciDB Language Query
        :return: QueryResult object
        """
        # array_name, min_x, min_y, min_t,  max_x, max_y, max_t):
        scidb = SciDB()

        query = scidb.executeQuery(query=statement, lang=lang)

        # Lets parallel the processing to get scidb data
        # Get SciDB Description
        desc = query.array.getArrayDesc()

        # Get SciDB Attributes reference
        attrs = desc.getAttributes()

        # List of processes
        processes = []

        # Prepare to get scidb iterators. It will be a list of tuple like [(band_name, iterator, band_scidb_type)]
        attributes = []

        # numpy dtype
        self.dtypes = []

        # SLOWWWW
        st = datetime.now()

        # Initialize a shared object to store each process response
        queue = Queue()

        for i in xrange(attrs.size()):
            if attrs[i].getName() != "EmptyTag":
                # process = Thread(target=self._get_iterators_from_scidb, args=(query, attrs, i, attributes, self.dtypes))
                # process = Process(target=self._get_iterators_from_scidb, args=(query, attrs, i, queue))
                # processes.append(process)
                # process.start()
        #
        # for i in xrange(attrs.size()):
        #     att, dtype = queue.get()
        #     attributes.append(att)
        #     self.dtypes.extend(dtype)

        # for process in processes:
        #     process.join()
                name = attrs[i].getName()
                iterator = query.array.getConstIterator(i)
                attribute_type = attrs[i].getType()
                attributes.append((name, iterator, attribute_type))
                self.dtypes.append((name, attribute_type))

        del processes[:]
        ed = datetime.now() - st
        print("Query IT -> "+str(ed))

        size = len(attributes)

        # Set scidb attributes
        self.attributes = [lst[0] for lst in attributes]

        begin = datetime.now()

        x, y, z = (self.col_id[1] - self.col_id[0] + 1,
                   self.row_id[1] - self.row_id[0] + 1,
                   self.time_id[1] - self.time_id[0] + 1)

        # Result to NumpyArray - Generate numpy zeros
        array = np.zeros((x, y, z), self.dtypes)

        # Start the multiprocessing list
        # It is main iterator
        while not attributes[0][1].end():
            for i in xrange(size):
                process = Process(target=self._parallel_getter_object, args=(attributes[i], queue))
                processes.append(process)
                process.start()

            # Retrieves data of each process
            for i in xrange(size):
                band, values = queue.get()
                # self.data[band].append(tuple(values))
                print("{} -> {}".format(band, len(values)))
                self.data[band].extend(values)

            # Wait for each process to join
            for i in xrange(size):
                processes[i].join()

            # Increment each one scidb iterator and break the loop
            for i in xrange(size):
                attributes[i][1].increment_to_next()

        # Set bands to nparray
        for attribute in self.attributes:
            band_arr = np.array(self.data[attribute]).reshape((x, y, z))
            # band_arr = np.array(self.data[attribute]).reshape((z, y * x)).T.reshape((x, y, z))
            array[attribute] = band_arr

        end = datetime.now() - begin

        del self.data
        self.data = array
        print("Time spend to retrieve scidb data: {}".format(str(end)))

        return query
        # from scidbpy import connect
        #
        # sdb = connect('http://localhost:8080')
        # afl = sdb.afl
        #
        # data = afl.subarray(array_name, min_x, min_y, min_t, max_x, max_y, max_t)
        # cls.attributes = data.att_names

        # return data

    def describe_coverage(self, params):
        coverages_ids = params.get('coverageid', [])
        if not coverages_ids:
            raise MissingParameterValue("Missing coverageID parameter", locator="coverageID", version="2.0.1")
        coverages_ids = ",".join(coverages_ids).split(",")
        self.geo_arrays = GeoArray.objects.filter(name__in=coverages_ids)
        if not self.geo_arrays:
            raise NoSuchCoverageException()

    def get_coverage(self, coverageid, subset=None, rangesubset=None, format="GML", inputcrs=4236,
                     outputcrs=4326):
        if not coverageid:
            raise MissingParameterValue("Missing coverageID parameter", locator="coverageID", version="2.0.1")
        if len(coverageid) > 1:
            raise InvalidParameterValue("Invalid coverage with id \"%s\"" % "".join(coverageid), locator="coverageID", version="2.0.1")
        try:
            self.geo_array = GeoArray.objects.get(name=coverageid[0])
            if subset:
                subset = self._get_subset_from(subset)
            self.col_id = subset.get('col_id', {}).get('dimension', self.geo_array.get_x_dimension())
            self.row_id = subset.get('row_id', {}).get('dimension', self.geo_array.get_y_dimension())
            time_id = subset.get('time_id', {}).get('dimension', self.geo_array.get_min_max_time())
            times_day_year = [DateToPoint.format_to_day_of_year(d) for d in time_id]

            del time_id

            start_date = self.geo_array.t_min.strftime('%Y-%m-%d')
            validator = DateToPoint(dt=start_date, period=self.geo_array.t_resolution,
                                    startyear=int(start_date[:4]),
                                    startday=int(DateToPoint.format_to_day_of_year(start_date)[4:]))

            self.time_id = [validator(t) for t in times_day_year]

            afl = "subarray({}, {}, {}, {}, {}, {}, {})".format(self.geo_array.name,
                                                                self.col_id[0], self.row_id[0],
                                                                self.time_id[0], self.col_id[1],
                                                                self.row_id[1],self.time_id[1])

            # Check if there are any range subset and if it is valid
            if rangesubset:
                bands = self._get_bands_from(rangesubset)

                # Make query to get only specified bands.
                afl = "project({}, {})".format(afl, ",".join(bands))

            # Do SciDB query and retrieve query reference. The scidb data is stored on data variable. (self.data)
            self.query = self.get_scidb_data(afl)

            # # Result to NumpyArray - Generate numpy zeros
            # array = np.zeros((x, y, z), self.dtypes)

            # bands = self.attributes
            self.bands = self.attributes

            # SciDBPY - data to numpy array
            # self.data = self.query.toarray()

        except ObjectDoesNotExist:
            raise NoSuchCoverageException()
        except ValueError as e:
            raise InvalidParameterValue("Invalid parameter \"%s\"" % e.message, locator="subset", version="2.0.1")
        except (IndexError, InvalidParameterValue) as e:
            raise e
        except SciDBConnectionError as e:
            raise e
        except InvalidRangeSubSet as e:
            raise e
        except Exception as e:
            print(e)
            raise WCSException(e, locator="request")

    def get_geo_array(self, array=None):
        geo = None
        if array:
            for c in self.geo_arrays:
                if c.name == array:
                    geo = c
                    break
        else:
            geo = self.geo_array
        if not geo:
            raise NoSuchCoverageException("No such coverage with ID \"%s\"" % array)
        return geo