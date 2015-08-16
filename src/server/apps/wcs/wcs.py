from django.core.exceptions import ObjectDoesNotExist
from apps.scidb.db import SciDB, scidbapi
from apps.scidb.exception import SciDBConnectionError
from exception import NoSuchCoverageException, InvalidSubset, InvalidAxisLabel, InvalidRangeSubSet, WCSException
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
    bands = None
    attributes = None

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

    @classmethod
    def get_scidb_data(cls, query, lang="AFL"):
        connection = SciDB(**DBConfig().get_scidb_credentials())
        result = connection.executeQuery(str(query), lang)
        cls.attributes = connection.attributes
        print(query)

        arraylist = []

        for res in connection.result_set:
            key, value = res
            arraylist.append({"index": key, "values": value})

        connection.completeQuery(result.queryID)
        connection.disconnect()

        return arraylist

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
        # coverage_id = params.get('coverageid', [])
        if not coverageid:
            raise MissingParameterValue("Missing coverageID parameter", locator="coverageID", version="2.0.1")
        if len(coverageid) > 1:
            raise InvalidParameterValue("Invalid coverage with id \"%s\"" % "".join(coverageid), locator="coverageID", version="2.0.1")
        try:
            self.geo_array = GeoArray.objects.get(name=coverageid[0])
            # self.bands_input = [band.name for band in self.geo_array.geoarrayattribute_set.all()]
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

            afl = "subarray(%s, %s, %s, %s, %s, %s, %s)" % (self.geo_array.name, self.col_id[0], self.row_id[0],
                                                            self.time_id[0], self.col_id[1], self.row_id[1],
                                                            self.time_id[1])

            data = self.get_scidb_data(afl)
            # bands = self.attributes
            self.bands = self.attributes

            if rangesubset:
                self._get_bands_from(rangesubset)
            self.data = {
                "limits": [data[0]['index'], data[-1]['index']],
                "values": {}
            }

            for band_name in self.bands:
                index = self.attributes.index(band_name)
                self.data['values'][band_name] = []
                for values in data:
                    self.data['values'][band_name].append(values['values'][index])
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