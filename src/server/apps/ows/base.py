from lxml import etree
from utils import namespace_xsi
from exception import InvalidParameterValue


class XMLEncoder(object):
    def serialize(self, tree, encoding='iso-8859-1'):
        schema_locations = self.get_schema_locations()
        tree.attrib[namespace_xsi("schemaLocation")] = " ".join("%s %s" % (uri, loc)
                                                                for uri, loc in schema_locations.items())

        return etree.tostring(tree, pretty_print=True, encoding=encoding)

    @property
    def content_type(self):
        return "application/xml"

    def get_schema_locations(self):
        """ Interface method. It must retrieves a dict of schema locations """
        return {}


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