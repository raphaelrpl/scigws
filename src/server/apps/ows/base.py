from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from django.http.request import QueryDict
from lxml import etree
from utils import namespace_xsi
from exception import InvalidParameterValue


class XMLEncoder(object):
    def serialize(self, tree, encoding='iso-8859-1'):
        if isinstance(tree, Element):
            return ElementTree.tostring(tree)
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
    _supported_versions = ["2.0.0", "2.0.1", "1.3.0"]
    _supported_operations = ["getcapabilities", "describecoverage", "getcoverage", "getmap", "getfeatureinfo"]

    def __init__(self, key_to_list_mapping):
        if isinstance(key_to_list_mapping, QueryDict):
            to_iterate, key_to_list_mapping = key_to_list_mapping, {}
            for key, value in to_iterate.iteritems():
                key_to_list_mapping[key.lower()] = [i.lower() for i in to_iterate.getlist(key)]
        if isinstance(key_to_list_mapping, basestring):
            # TODO: XML Request
            from xmltodict import parse as xml_to_dict
            from json import dumps as json_dumps, loads as json_loads
            data = xml_to_dict(key_to_list_mapping)
            dct = json_loads(json_dumps(data))

            def iterate_dict(nested):
                for key, value in nested.iteritems():
                    if isinstance(value, dict):
                        for inner_key, inner_value in iterate_dict(value):
                            yield inner_key, inner_value
                    else:
                        yield key, value

            list_elements = list(iterate_dict(dct))
            k = dct.keys()[0].lower()
            request = k if ':' not in k else k.split(':')[1]
            key_to_list_mapping = {'request': [request]}
            for element in list_elements:
                if element[0].lower() == "@service" or element[0].lower() == "@version":
                    key_to_list_mapping[element[0][1:].lower()] = [element[1].lower()]
                elif not element[0].startswith('@'):
                    e = element[0].lower()
                    if ':' in e:
                        e = e.split(':')[1].lower()
                    key_to_list_mapping[e] = [element[1].lower()]
        super(OWSDict, self).__init__(key_to_list_mapping)
        self._is_valid_ows_request()
        self.coverage_id_formatter()

    def _is_valid_ows_request(self):
        service = self.get('service', ' ')
        # service = service if isinstance(service, basestring) else service[0]
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

    def coverage_id_formatter(self):
        coverages = filter(bool, self.get('coverageid', []))
        if coverages:
            del self['coverageid']
            output = []
            for coverage in coverages:
                if ',' in coverage:
                    for c in coverage.split(','):
                        output.append(c)
                else:
                    output.append(coverage)
            self['coverageid'] = output
            return
        if "coverageid" in self.keys():
            raise InvalidParameterValue("Invalid coverage identifier", locator="coverageID")


class BaseHandler(object):
    @classmethod
    def handle(cls, handler, **kwargs):
        """ It must be implemented """


class BaseFactory(object):
    @staticmethod
    def factory(params):
        """ It must be implemented """