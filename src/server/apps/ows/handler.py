from encoders import OWSExceptionResponse
from exception import InvalidParameterValue
from apps.wcs.encoders import GetCapabilitiesEncoder, DescribeCoverageEncoder, GetCoverageEncoder
from base import OWSDict


class RequestHandler(object):
    @classmethod
    def handle(cls, request):
        if request.method == "GET":
            service_request = OWSDict(request.GET)
        else:
            service_request = OWSDict(request.body)
        return OWSFactory.factory(service_request)


class OWSExceptionHandler(object):
    @classmethod
    def handle(cls, exception):
        message = exception.message
        version = "2.0.1"
        code = getattr(exception, "code", None) or "NoApplicableCode"
        locator = getattr(exception, "locator", None)

        response = OWSExceptionResponse()

        return response.serialize(response.dispatch(message=message, version=version, code=code,
                                                    locator=locator)), response.content_type


class WCSFactory(object):
    @staticmethod
    def factory(params):
        request = params.get('request', [''])[0]
        if request == "getcapabilities":
            return GetCapabilitiesEncoder(params)
        if request == "describecoverage":
            return DescribeCoverageEncoder(params)
        if request == "getcoverage":
            return GetCoverageEncoder(params)
        raise InvalidParameterValue("Invalid request name \"%s\"" % request, locator="request")


class WMSFactory(object):
    @staticmethod
    def factory(params):
        return


class OWSFactory(object):
    @staticmethod
    def factory(params):
        if isinstance(params, OWSDict):
            request, service = params.get_ows_request()
            if service == "wcs":
                return WCSFactory.factory(params)
            elif params.get_ows_request() == "wms":
                return WMSFactory.factory(params)
            raise InvalidParameterValue("Invalid service name", locator="service")
        raise InvalidParameterValue("Invalid request name")