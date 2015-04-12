from encoders import OWSExceptionResponse
from apps.wcs.encoders import GetCapabilitiesEncoder


class ServiceRequest(object):
    params = {}

    def __init__(self, params):
        if isinstance(params, dict):
            for key, value in params.iteritems():
                self.params[key.lower()] = value.lower()

    def __str__(self):
        return "<ServiceRequest {}>".format(self.params)
    


class RequestHandler(object):
    @classmethod
    def handle(cls, request):
        if request.method == "GET":
            service_request = ServiceRequest(request.GET)
        else:
            service_request = ServiceRequest(request.body)
        return OWSFactory.factory(service_request.params)


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


class OWSFactory(object):
    @staticmethod
    def factory(params):
        if isinstance(params, dict):
            service = params.get('service', "")
            if service.lower() == "wcs":
                return GetCapabilitiesEncoder()
            elif service.lower() == "wms":
                pass
            raise OWSException("Invalid service name")  # fix this