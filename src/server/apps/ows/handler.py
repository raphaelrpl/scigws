from django.http.request import QueryDict
from encoders import OWSExceptionResponse


class ServiceRequest(object):
    params = {}

    def __init__(self, params):
        if isinstance(params, QueryDict):
            for key, value in params.iteritems():
                params[key.lower()] = value.lower()


a = ServiceRequest({'NAME': "Abacate", 'service': "WCS"})


class RequestHandler(object):
    @classmethod
    def handle(cls, request):
        """ output xml """
        if request.method == "GET":
            service_request = ServiceRequest(request.GET)
        else:
            service_request = ServiceRequest(request.body)


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