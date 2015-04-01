import psycopg2

from django.http import HttpResponse
from django.views.generic.base import View
from apps.wcs.wcs import GetCapabilities, DescribeCoverage, GetCoverage
from apps.wcs.exception import throws_exception
from utils import get_scidb_credentials
from apps.scidb.db import SciDB, scidbapi


class SimpleView(View):
    def process_request(self, request):
        wcs_errors = {}
        service = request.GET.get('service', '') or request.GET.get('SERVICE')
        if service and service.lower() == "wcs":
            version = request.GET.get('version', ' ') or request.GET.get('VERSION', ' ')
            if version and (1 or version == '2.0.0' or version == '2.0.1'):
                req = request.GET.get("request") or request.GET.get("REQUEST")
                if hasattr(req, 'lower'):
                    if req.lower() in ["getcapabilities", "describecoverage", "getcoverage", ""]:
                        params = {"service": service, "version": version, "request": req}
                        scidb_config = get_scidb_credentials()
                        if scidb_config:
                            psql_connection = psycopg2.connect(host="localhost", user="postgres", port=5433, database="modis_metadata")
                            cursor = psql_connection.cursor()
                            cursor.execute("SELECT * FROM geo_array")
                            results = cursor.fetchall()
                            geo_arrays = []
                            if results:
                                for result in results:
                                    geo_arrays.append(result[1])
                            scidb_connection = SciDB(str(scidb_config.get('host')), scidb_config.get('port'))
                            query = scidb_connection.executeQuery("list('arrays')")
                            attributes = query.array.getArrayDesc().getAttributes()
                            attributes = [attributes[i] for i in range(attributes.size()) if attributes[i].getName() != "EmptyTag"]
                            attribute_iterators = [query.array.getConstIterator(attribute.getId()) for attribute in attributes]
                            coverages_offered = []
                            while not attribute_iterators[0].end():
                                value_iterator = attribute_iterators[0].getChunk().getConstIterator(
                                    scidbapi.swig.ConstChunkIterator.IGNORE_OVERLAPS |
                                    scidbapi.swig.ConstChunkIterator.IGNORE_EMPTY_CELLS)
                                while not value_iterator.end():
                                    if value_iterator.getItem().getString() in geo_arrays:
                                        coverages_offered.append(value_iterator.getItem().getString())
                                    value_iterator.increment_to_next()
                                attribute_iterators[0].increment_to_next()
                                del value_iterator
                            scidb_connection.disconnect()
                            del scidb_connection, attribute_iterators, query, attributes, geo_arrays
                            if params['request'].lower() == "getcapabilities" or not req:
                                cursor.close()
                                psql_connection.close()
                                capabilities = GetCapabilities("http://%s?" % (
                                    request.get_host()+request.path), coverages_offered=coverages_offered)
                                xml_output, code = capabilities.get_capabilities()
                                return HttpResponse(xml_output, content_type="application/xml", status=code)
                            elif params['request'].lower() == "describecoverage":
                                cursor.execute("SELECT array_id, date FROM geo_array_timeline")
                                times = cursor.fetchall()
                                cursor.execute("SELECT * FROM geo_array_attributes")
                                attributes = cursor.fetchall()
                                describe = DescribeCoverage(params, coverages_offered, results, attributes, times)
                                xml_output, code = describe.describe_coverage(request.GET.get("coverageId", ""))
                                cursor.close()
                                psql_connection.close()
                                del cursor, attributes
                                return HttpResponse(xml_output, content_type="application/xml", status=code)
                            elif params['request'].lower() == "getcoverage":
                                coverage = GetCoverage(params, coverages_offered, results)
                                coverage_params = {str(key).lower(): request.GET.get(key) for key in request.GET.keys() if str(key).lower() not in params.keys() and str(key) != "coverageId"}
                                coverage_params["subset"] = request.GET.getlist('subset')
                                xml_output, code, content = coverage.get_coverage(coverageId=request.GET.get('coverageId', ''), **coverage_params)
                                return HttpResponse(xml_output, content_type=content, status=code)
                            cursor.close()
                            psql_connection.close()
                            del coverages_offered, attribute_iterators, attributes, query, results, geo_arrays, req
                        wcs_errors['message'] = "SciDB configuration not found, insert into database"
                        wcs_errors['exceptionCode'] = "InvalidParameterValue"
                        wcs_errors['param'] = request.GET.get('request', '')
                    else:
                        wcs_errors['message'] = "Invalid REQUEST parameter"
                        wcs_errors['exceptionCode'] = "InvalidParameterValue"
                        wcs_errors['param'] = request.GET.get('request', '')
                else:
                    wcs_errors['message'] = "Missing REQUEST parameter"
                    wcs_errors['exceptionCode'] = "MissingParameterValue"
                wcs_errors['locator'] = 'request'
            else:
                wcs_errors['message'] = "Invalid version"
                wcs_errors['locator'] = 'version'
                wcs_errors['exceptionCode'] = "InvalidParameterValue"
                wcs_errors['param'] = version
        else:
            wcs_errors['message'] = "Invalid service name"
            wcs_errors['locator'] = 'service'
            wcs_errors['exceptionCode'] = "InvalidParameterValue"
            wcs_errors['param'] = service

        del service
        return HttpResponse(throws_exception({
            "message": wcs_errors.get("message"),
            "exceptionCode": wcs_errors.get("exceptionCode"),
            "locator": wcs_errors.get("locator"),
            "param": "%s" % wcs_errors.get("param") if wcs_errors.get('param') is not None else ""
        }), content_type="application/xml", status=400)

    def get(self, request):
        return self.process_request(request)

    def post(self, request):
        return self.process_request(request)