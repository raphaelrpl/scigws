from xml.etree import ElementTree
from apps.ows.ows_old import OWSMeta
from exception import throws_exception
from apps.scidb.db import SciDB, scidbapi
from exception import WCSException
from utils import pretty_xml
from validators import DateToPoint
from base import WCSBase
from apps.swe.swe import SWEMeta
from validators import is_valid_url
from apps.gml.gml import GMLMeta
from datetime import datetime
from apps.geo.models import GeoArrayTimeLine, GeoArray


class GetCapabilities(WCSBase):
    attrib = {
        "xmlns:xsi": 'http://www.w3.org/2001/XMLSchema-instance',
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
        "xmlns": "http://www.opengis.net/ows/2.0",
        "xmlns:wcseo": "http://www.opengis.net/wcseo/1.0",
        "xmlns:ows": "http://www.opengis.net/ows/2.0",
        "xsi:schemaLocation": "http://www.opengis.net/wcs/wcseo/1.0 http://schemas.opengis.net/wcs/wcseo/1.0/wcsEOAll.xsd http://www.opengis.net/wcs/2.0 http://schemas.opengis.net/wcs/2.0/wcsAll.xsd",
        "version": "2.0.1"
    }
    config = None
    scidb_arrays = None
    metadata = None

    def __init__(self, url="http://localhost:8000/ows?", coverages_offered=[]):
        super(GetCapabilities, self).__init__()
        self.url = url
        self.initialize_metadata()
        self.coverages_offered = coverages_offered

    def _create_dom(self):
        return ElementTree.Element("{http://www.opengis.net/wcs/2.0}Capabilities", attrib=self.attrib)

    def initialize_metadata(self):
        self.metadata = OWSMeta()
        self.metadata.generate_profiles()
        self.metadata.generate_operations(self.url)
        self.dom.append(self.metadata.root_identification)
        self.service_identification = self.metadata.root_identification
        self.dom.append(self.metadata.root_provider)
        self.service_provider = self.metadata.root_provider
        self.dom.append(self.metadata.root_operations)
        self.service_metadata = ElementTree.SubElement(self.dom, "{%s}ServiceMetadata" % self.ns_dict['wcs'])
        format1 = ElementTree.SubElement(self.service_metadata, "{%s}formatSupported" % self.ns_dict['wcs']).text = "application/gml+xml"
        format2 = ElementTree.SubElement(self.service_metadata, "{%s}formatSupported" % self.ns_dict['wcs']).text = "image/tiff"

    def get_capabilities(self):
        self.contents = ElementTree.SubElement(self.dom, "{%s}Contents" % self.ns_dict['wcs'])
        self.coverages = {}
        for coverage in self.coverages_offered:
            sumary = ElementTree.SubElement(self.contents, "{%s}CoverageSummary" % self.ns_dict['wcs'])
            self.coverages[self.geo_arrays[coverage].get('name')] = {
                "id": ElementTree.SubElement(sumary, "{%s}CoverageId" % self.ns_dict['wcs']),
                "subtype": ElementTree.SubElement(sumary, "{%s}CoverageSubtype" % self.ns_dict['wcs'])
            }
            self.coverages[self.geo_arrays[coverage].get('name')]["id"].text = self.geo_arrays[coverage].get('name')
            self.coverages[self.geo_arrays[coverage].get('name')]["subtype"].text = "GridCoverage"

        if self.config is None:
            raise WCSException("DB config is empty! \"%s\"" % self.config)

        # Check time series available in scidb, get metadata from postgres
        results = GeoArrayTimeLine.objects.all()

        for coverage in self.geo_arrays:
            dataseries = ElementTree.SubElement(self.dom, "wcseo:DatasetSeriesSummary")
            dataid = ElementTree.SubElement(dataseries, "wcseo:DatasetSeriesId")
            dataid.text = str(self.geo_arrays[coverage].get('name'))
            # time_period = ElementTree.SubElement(dataseries, "{%s}TimePeriod" % self.ns_dict['gml'])
            temporal = ElementTree.SubElement(dataseries, "{%s}TemporalDomain" % self.ns_dict['wcs'])
            for result in results:
                if self.geo_arrays[coverage].get('name') == result.array.name:
                    tree = ElementTree.SubElement(temporal, "{%s}timePosition" % self.ns_dict['gml'])
                    tree.text = result.date.strftime("%Y-%m-%d")
        return pretty_xml(self.dom), 200


class DescribeCoverage(WCSBase):
    attrib = {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns": "http://www.opengis.net/gml/3.2",
        "xmlns:swe": "http://www.opengis.net/swe/2.0",
        "xsi:schemaLocation": """http://www.opengis.net/swe/2.0 http://schemas.opengis.net/sweCommon/2.0/swe.xsd
         http://www.opengis.net/wcs/2.0 http://schemas.opengis.net/wcs/2.0/wcsAll.xsd"""
    }
    coverages_offered = None
    metadatas = None

    def __init__(self, coverages_offered):
        super(DescribeCoverage, self).__init__()
        self.coverages_offered = coverages_offered
        self.metadatas = GeoArray.objects.filter(name__in=coverages_offered)

    def _create_dom(self):
        return ElementTree.Element("{http://www.opengis.net/wcs/2.0}CoverageDescriptions", attrib=self.attrib)

    def describe_coverage(self, identifiers):
        errors = {}
        code_error = 400
        if identifiers:
            coverages_name = identifiers.split(',')
            for identifier in coverages_name:
                if identifier in self.coverages_offered:
                    metadata = [meta for meta in self.metadatas if identifier == meta.name][0]
                    self.coverage_description = ElementTree.SubElement(self.dom, "{%s}CoverageDescription" %
                                                                       self.ns_dict['wcs'], attrib={"gml:id": identifier})
                    print(metadata)
                    times = metadata.geoarraytimeline_set.all()
                    print(times)

                    gml = GMLMeta(identifier, self.geo_arrays.get(identifier), times)
                    bounded = gml.get_bounded_by()
                    self.coverage_description.append(bounded)
                    self.coverage_id = ElementTree.SubElement(self.coverage_description,
                                                              "{%s}CoverageId" % self.ns_dict['wcs'])

                    self.coverage_id.text = identifier
                    self.domain_set = ElementTree.SubElement(self.coverage_description,
                                                             "{%s}domainSet" % self.ns_dict['gml'])

                    grid = gml.get_grid()
                    self.domain_set.append(grid)
                    self.temp_domain = ElementTree.SubElement(self.coverage_description,
                                                              "{%s}TemporalDomain" % self.ns_dict['wcs'])

                    self.times_domain = []
                    for timeposition in times:
                        # if timeposition[0] == metadata[0]:
                        tree = ElementTree.SubElement(self.temp_domain, "{%s}timePosition" % self.ns_dict['gml'])
                        # if isinstance(timeposition[1], datetime):
                        tree.text = timeposition.date.strftime("%Y-%m-%d")
                        self.times_domain.append(tree)

                    self.rangeType = ElementTree.SubElement(self.coverage_description,
                                                            "{%s}rangeType" % self.ns_dict['gmlcov'])

                    swe = SWEMeta(identifier=identifier, meta=self.geo_arrays.get(identifier))
                    self.data_record = swe.get_data_record()
                    self.rangeType.append(self.data_record)
                    self.service_parameters = ElementTree.SubElement(self.coverage_description,
                                                                     "{%s}ServiceParameters" % self.ns_dict['wcs'])

                    self.coverage_subtype = ElementTree.SubElement(self.service_parameters,
                                                                   "{%s}CoverageSubtype" % self.ns_dict['wcs'])

                    self.coverage_subtype.text = "GridCoverage"
                    self.native_format = ElementTree.SubElement(self.service_parameters,
                                                                "{%s}nativeFormat" % self.ns_dict['wcs'])

                    self.native_format.text = "application/gml+xml"
                    code_error = 200
                else:
                    errors["message"] = "Unknown coverage. "
                    errors["exceptionCode"] = "NoSuchCoverage"
                    errors['param'] = identifier
                    code_error = 404
                    break
            if code_error == 200:
                return pretty_xml(self.dom), code_error
        else:
            errors["message"] = "Missing COVERAGEID parameter."
            errors["exceptionCode"] = "MissingParameterValue"
        errors["locator"] = "coverage"
        if code_error == 400:
            errors["param"] = identifiers
        return throws_exception(errors), code_error


class GetCoverage(WCSBase):
    attrib = {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:swe": "http://www.opengis.net/swe/2.0",
        "xmlns": "http://www.opengis.net/gml/3.2",
        "xsi:schemaLocation": "http://www.opengis.net/wcs/2.0 http://schemas.opengis.net/wcs/2.0/wcsAll.xsd"
    }
    formats = ["application/xml", "application/gml+xml", "image/tiff", "GTiff"]
    metadata = None

    def __init__(self, coverages_offered, metadatas):
        super(GetCoverage, self).__init__()
        self.coverages_offered = coverages_offered
        self.metadatas = [metadata for metadata in metadatas if metadata.name in coverages_offered]

    def _create_dom(self):
        return ElementTree.Element("{http://www.opengis.net/gmlcov/1.0}GridCoverage", attrib=self.attrib)

    def _make_grid_envelope(self, root, attrib={}):
        return ElementTree.SubElement(root, "{%s}GridEnvelope" % self.ns_dict['gml'], attrib=attrib)

    def get_subset_from(self, subset):
        params = {}
        for element in subset:
            args = filter(None, element.split('(')[1].strip(')').split(','))
            if len(args) != 2:
                raise ValueError(element)
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
            print(self.metadata)
            if key != self.metadata.x_dim_name and key != self.metadata.y_dim_name and key != self.metadata.y_dim_name:
                raise ValueError("\"%s\" is not valid axis. " % sub)
        return params

    def get_data_from_db(self, query, lang="AFL"):
        connection = SciDB(str(self.config.get('scidb', {}).get('host')), self.config.get('scidb', {}).get('port'))
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

    def get_coverage(self, coverageId, subset=None, crs=None, format="application/xml"):
        errors = {}
        code_error = 400
        if coverageId:
            if coverageId in self.coverages_offered:
                self.dom.attrib['{%s}id' % self.ns_dict['gml']] = coverageId
                self.metadata = [meta for meta in self.metadatas if coverageId == meta.name][0]
                geo = self.geo_arrays[coverageId]
                if format in self.formats:
                    afl = ""
                    # times = self.get_times_db(self.metadata[0])
                    times = GeoArrayTimeLine.objects.filter(array__name=coverageId)
                    range_time = [
                        GeoArrayTimeLine.objects.filter(array__name=coverageId).first().time_point,
                        GeoArrayTimeLine.objects.filter(array__name=coverageId).last().time_point
                    ]
                    if subset:
                        try:
                            params = self.get_subset_from(subset)
                        except (ValueError, IndexError):
                            errors["message"] = "Invalid subset dimension"
                            errors["exceptionCode"] = "InvalidParameterValue"
                            errors["locator"] = "subset"
                            errors["param"] = subset
                            return throws_exception(errors), code_error, "application/xml"
                        col_id = (params.get('col_id', {}).get('dimension') or params.get('x', {}).get('dimension')) or [geo["x_min"], geo["x_max"]]
                        row_id = params.get('row_id', {}).get('dimension') or [geo["y_min"], geo["y_max"]]
                        if params.get('time_id'):
                            time_id = params.get('time_id', {}).get('dimension')
                            times_day_year = []
                            for t in time_id:
                                times_day_year.append(DateToPoint.format_to_day_of_year(t))
                            period = self.geo_arrays[coverageId].get('t_resolution')
                            start_date = self.geo_arrays[coverageId].get('t_min')
                            validator = DateToPoint(dt=start_date, period=period, startyear=int(start_date[:4]),
                                                    startday=datetime.strptime(start_date, '%Y-%M-%d').timetuple().tm_yday)
                            time_id = [validator(t) for t in times_day_year]
                            print(time_id)
                        else:
                            time_id = range_time
                        afl = "subarray(%s, %s, %s, %s, %s, %s, %s)" % (
                            coverageId,
                            col_id[0],
                            row_id[0],
                            time_id[0],
                            col_id[1],
                            row_id[1],
                            time_id[1]
                        )
                    else:
                        afl = "subarray(%s, %s, %s, %s, %s, %s, %s)" % (
                            coverageId,
                            geo["x_min"],
                            geo["y_min"],
                            range_time[0],
                            geo["x_max"],
                            geo["y_min"],
                            range_time[-1]
                        )
                    print "AFL Generated -> %s" % afl
                    gml = GMLMeta(identifier=coverageId, meta=geo, times=times)
                    bounded = gml.get_bounded_by()
                    self.dom.append(bounded)
                    if not times:
                        errors["message"] = "Invalid timeid for"
                        errors["exceptionCode"] = "InvalidParameterValue"
                        errors["locator"] = "subset"
                        errors["param"] = coverageId
                        return throws_exception(errors), code_error, "application/xml"

                    # DOMAIN SET
                    domain_set = ElementTree.SubElement(self.dom, "{%s}domainSet" % self.ns_dict['gml'])
                    grid = gml.get_grid()
                    domain_set.append(grid)

                    gml_range = ElementTree.SubElement(self.dom, "{%s}rangeSet" % self.ns_dict['gml'])
                    data_block = ElementTree.SubElement(gml_range, "{%s}DataBlock" % self.ns_dict['gml'])
                    tuple_list = ElementTree.SubElement(data_block, "{%s}tupleList" % self.ns_dict['gml'], attrib={
                        'ts': ',',
                        'cs': ' '
                    })
                    tuple_list.text = ''
                    res = self.get_data_from_db(str(afl))
                    for i in range(len(res.values()[0])):
                        for attr_dict in geo['attributes']:
                            tuple_list.text += "%i " % res[attr_dict['name']][i]
                        tuple_list.text = tuple_list.text.rstrip(" ") + ","
                    tuple_list.text = tuple_list.text.rstrip(',')
                    swe = SWEMeta(identifier=coverageId, meta=self.geo_arrays.get(coverageId))
                    swe_data_record = swe.get_data_record()
                    range_type = ElementTree.SubElement(self.dom, "{%s}rangeType" % self.ns_dict['gmlcov']).append(swe_data_record)
                    # self.dom.append(swe_data_record)
                    return pretty_xml(self.dom), 200, format
                errors["message"] = "Unknown/not supported format"
                errors["exceptionCode"] = "InvalidParameterValue"
                errors["locator"] = "format"
                errors["param"] = format
                return throws_exception(errors), code_error, "application/xml"
            else:
                errors["message"] = "Unknown coverage."
                errors["exceptionCode"] = "NoSuchCoverage"
                code_error = 404
        else:
            errors["message"] = "Missing COVERAGEID parameter."
            errors["exceptionCode"] = "MissingParameterValue"
        errors["locator"] = "coverage"
        errors["param"] = coverageId
        return throws_exception(errors), code_error, "application/xml"