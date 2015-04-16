from django.http import HttpResponse
from django.views.generic.base import View
from apps.wcs.wcs import GetCapabilities, DescribeCoverage, GetCoverage
from apps.wcs.exception import throws_exception
from utils import DBConfig
from apps.scidb.db import SciDB, scidbapi
from apps.geo.models import GeoArray
from handler import RequestHandler, OWSExceptionHandler


class SimpleView(View):
    def process_request(self, request):
        code = 200
        try:
            result = RequestHandler.handle(request)
            return HttpResponse(result.serialize(result.encode(request)), content_type=result.content_type, status=code)
        except Exception as e:
            result, content_type = OWSExceptionHandler.handle(e)
            code = 400
            return HttpResponse(result, content_type=content_type, status=code)

        wcs_errors = {}
        service = request.GET.get('service', '') or request.GET.get('SERVICE')
        if service and service.lower() == "wcs":
            version = request.GET.get('version', ' ') or request.GET.get('VERSION', ' ')
            if version and (1 or version == '2.0.0' or version == '2.0.1'):
                req = request.GET.get("request") or request.GET.get("REQUEST")
                if hasattr(req, 'lower'):
                    if req.lower() in ["getcapabilities", "describecoverage", "getcoverage", ""]:
                        params = {"service": service, "version": version, "request": req}
                        scidb_config = DBConfig().scidb

                        if scidb_config:
                            results = GeoArray.objects.all()
                            array_names = [r.name for r in results]

                            scidb_connection = SciDB(**scidb_config)
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
                                    if value_iterator.getItem().getString() in array_names:
                                        coverages_offered.append(value_iterator.getItem().getString())
                                    value_iterator.increment_to_next()
                                attribute_iterators[0].increment_to_next()
                                del value_iterator
                            scidb_connection.disconnect()
                            if params['request'].lower() == "getcapabilities" or not req:
                                capabilities = GetCapabilities("http://%s?" % (
                                    request.get_host()+request.path), coverages_offered=coverages_offered)
                                xml_output, code = capabilities.get_capabilities()
                                return HttpResponse(xml_output, content_type="application/xml", status=code)
                            elif params['request'].lower() == "describecoverage":

                                describe = DescribeCoverage(coverages_offered)
                                xml_output, code = describe.describe_coverage(request.GET.get("coverageID", ""))
                                return HttpResponse(xml_output, content_type="application/xml", status=code)
                            elif params['request'].lower() == "getcoverage":
                                
                                coverage = GetCoverage(coverages_offered, results)
                                coverage_params = {str(key).lower(): request.GET.get(key) for key in request.GET.keys() if str(key).lower() not in params.keys() and str(key) != "coverageId"}
                                coverage_params["subset"] = request.GET.getlist('subset')
                                xml_output, code, content = coverage.get_coverage(coverageId=request.GET.get('coverageId', ''), **coverage_params)
                                return HttpResponse(xml_output, content_type=content, status=code)
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