from django.core.exceptions import ObjectDoesNotExist
from apps.scidb.db import SciDB, scidbapi
from apps.scidb.exception import SciDBConnectionError
from exception import NoSuchCoverageException, InvalidSubset, InvalidAxisLabel
from utils import WCS_MAKER
from validators import DateToPoint
from validators import is_valid_url
from apps.geo.models import GeoArrayTimeLine, GeoArray
from apps.ows.utils import DBConfig
from collections import defaultdict
from apps.ows.exception import MissingParameterValue, InvalidParameterValue


class WCS(object):
    geo_array = None
    data = {}

    def __init__(self, formats=[]):
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
                raise InvalidAxisLabel("\"%s\" is not valid axis. " % sub, locator="subset")
        return params

    @classmethod
    def get_scidb_data(cls, query, lang="AFL"):
        connection = SciDB(**DBConfig().get_scidb_credentials())
        result = connection.executeQuery(str(query), lang)
        desc = result.array.getArrayDesc()
        attributes = desc.getAttributes()
        attributes = [attributes[i] for i in range(attributes.size()) if attributes[i].getName() != "EmptyTag"]
        attribute_iterators = [[attribute.getName(), attribute.getType(),
                                result.array.getConstIterator(attribute.getId())] for attribute in attributes]
        output = {}
        dimensions = desc.getDimensions()
        dnames = []
        for i in range(dimensions.size()):
            if dimensions[i].getBaseName() != "EmptyTag":
                dnames.append(dimensions[i].getBaseName())
        for iterator in attribute_iterators:
            values = []
            while not iterator[2].end():
                value_iterator = iterator[2].getChunk().getConstIterator(
                    scidbapi.swig.ConstChunkIterator.IGNORE_OVERLAPS |
                    scidbapi.swig.ConstChunkIterator.IGNORE_EMPTY_CELLS)
                while not value_iterator.end():
                    values.append(scidbapi.getTypedValue(value_iterator.getItem(), iterator[1]))
                    value_iterator.increment_to_next()
                try:
                    iterator[2].increment_to_next()
                except:
                    pass
            output[iterator[0]] = values
        connection.completeQuery(result.queryID)
        connection.disconnect()
        return output

    def describe_coverage(self, params):
        coverages_ids = params.get('coverageid', [])
        if not coverages_ids:
            raise MissingParameterValue("Missing coverageID parameter", locator="coverageID")
        coverages_ids = ",".join(coverages_ids).split(",")
        self.geo_arrays = GeoArray.objects.filter(name__in=coverages_ids)
        if not self.geo_arrays:
            raise NoSuchCoverageException()

    def get_coverage(self, params):
        coverage_id = params.get('coverageid', [])
        if not coverage_id:
            raise MissingParameterValue("Missing coverageID parameter", locator="coverageID")
        if len(coverage_id) > 1:
            raise InvalidParameterValue("Invalid coverage with id \"%s\"" % "".join(coverage_id), locator="coverageID")
        try:
            self.geo_array = GeoArray.objects.get(name=coverage_id[0])
            subset_list = params.get('subset', [])
            subset = self._get_subset_from(subset_list)
            col_id = subset.get('col_id', {}).get('dimension', self.geo_array.get_x_dimension())
            row_id = subset.get('row_id', {}).get('dimension', self.geo_array.get_y_dimension())
            time_id = subset.get('time_id', {}).get('dimension', self.geo_array.get_min_max_time())
            times_day_year = [DateToPoint.format_to_day_of_year(d) for d in time_id]

            del time_id

            start_date = self.geo_array.t_min.strftime('%Y-%m-%d')
            validator = DateToPoint(dt=start_date, period=self.geo_array.t_resolution,
                                    startyear=int(start_date[:4]),
                                    startday=int(DateToPoint.format_to_day_of_year(start_date)[4:]))

            time_id = [validator(t) for t in times_day_year]

            afl = "subarray(%s, %s, %s, %s, %s, %s, %s)" % (self.geo_array.name, col_id[0], row_id[0], time_id[0],
                                                            col_id[1], row_id[1], time_id[1])

            # Get SciDB data - Time series
            self.data = self.get_scidb_data(afl)

        except ObjectDoesNotExist:
            raise NoSuchCoverageException()
        except ValueError as e:
            raise InvalidParameterValue("Invalid parameter \"%s\"" % e.message, locator="subset")
        except (IndexError, InvalidParameterValue) as e:
            raise e
        except SciDBConnectionError as e:
            raise e
        except Exception as e:
            print(e)
            raise InvalidSubset()

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