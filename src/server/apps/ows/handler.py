from apps.wms.encoders import WMSGetCapabilitiesEnconder
from apps.wms.wms import WMS
from encoders import OWSExceptionResponse
from exception import InvalidParameterValue
from apps.wcs.encoders import GetCapabilitiesEncoder, DescribeCoverageEncoder, GetCoverageEncoder, WCSEncoder
from base import OWSDict


class RequestHandler(object):
    @classmethod
    def handle(cls, request):
        if request.method == "GET":
            service_request = OWSDict(request.GET)
        else:
            service_request = OWSDict(request.body)
        return OWSFactory.factory(service_request)


class OWSFactory(object):
    service = ""

    @staticmethod
    def factory(params):
        if isinstance(params, OWSDict) or issubclass(params, OWSDict):
            request, service = params.get_ows_request()
            for factory_class in type.__subclasses__(OWSFactory):
                if factory_class.service == service:
                    return factory_class.factory(params)
            raise InvalidParameterValue("Invalid service name", locator="service")
        raise InvalidParameterValue("Invalid request name", locator="request")


class OWSExceptionHandler(object):
    @classmethod
    def handle(cls, exception):
        message = exception.message

        version = getattr(exception, "version", "1.3.0")
        code = getattr(exception, "code", None) or "NoApplicableCode"
        locator = getattr(exception, "locator", None)

        response = OWSExceptionResponse()

        return response.serialize(response.dispatch(message=message, version=version, code=code,
                                                    locator=locator)), response.content_type


class WCSFactory(OWSFactory):
    service = "wcs"

    @staticmethod
    def factory(params):
        request = params.get('request', [''])[0]
        for klass in type.__subclasses__(WCSEncoder):
            if klass.request.lower() == request:
                return klass(params)
        raise InvalidParameterValue("Invalid request name \"%s\"" % request, locator="request", version='2.0.1')


class WMSFactory(OWSFactory):
    service = "wms"

    @staticmethod
    def factory(params):
        request = params.get('request', [''])[0]
        if request == "getcapabilities":
            return WMSGetCapabilitiesEnconder(params)
        if request == "getmap":
            return
        if request == "getfeatureinfo":
            return
        raise InvalidParameterValue("Invalid request name \"%s\"" % request, locator="request", version='1.3.0')