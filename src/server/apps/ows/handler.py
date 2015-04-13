from encoders import OWSExceptionResponse
from exception import InvalidParameterValue
from apps.wcs.encoders import GetCapabilitiesEncoder, DescribeCoverageEncoder


class OWSDict(dict):
    _supported_services = ["wcs", "wms"]
    _supported_versions = ["2.0.0", "2.0.1"]
    _supported_operations = ["getcapabilities", "describecoverage", "getcoverage", "getmap", "getlayer"]

    def __init__(self, key_to_list_mapping):
        if isinstance(key_to_list_mapping, dict):
            key_to_list_mapping._mutable = True
            to_iterate = key_to_list_mapping.copy()
            for key, value in to_iterate.iteritems():
                key_to_list_mapping[key.lower()] = value.lower()
        super(OWSDict, self).__init__(key_to_list_mapping)
        self._is_valid_ows_request()

    def __str__(self):
        return "<ServiceRequestDict {}>".format(self)

    def _is_valid_ows_request(self):
        service = self.get('service', ' ')
        if service[0] not in self._supported_services:
            raise InvalidParameterValue("Invalid service name", locator="service")
        version = self.get('version', ['2.0.1'])
        if version[0] not in self._supported_versions:
            raise InvalidParameterValue("Invalid version name", locator="version")
        request = self.get('request', ' ')
        if request[0] not in self._supported_operations:
            raise InvalidParameterValue("Invalid request name", locator="request")

    def get_ows_request(self):
        req = self.get('request', '')
        service = self.get('service', '')
        return req[0].lower(), service[0].lower() if req and service else None


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


class OWSFactory(object):
    @staticmethod
    def factory(params):
        if isinstance(params, OWSDict):
            request, service = params.get_ows_request()
            if service == "wcs":
                if request == "getcapabilities":
                    return GetCapabilitiesEncoder(params)
                if request == "describecoverage":
                    return DescribeCoverageEncoder(params)
                if request == "getcoverage":
                    pass
                raise InvalidParameterValue("Invalid request name", locator="request")
            elif params.get_ows_request() == "wms":
                pass
            raise InvalidParameterValue("Invalid service name", locator="service")  # fix this