from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from django.http.request import QueryDict
from lxml import etree
from utils import namespace_xsi
from exception import InvalidParameterValue
import multiprocessing


class OWSEncoder(object):
    content_type = None

    def serialize(self):
        pass


class XMLEncoder(OWSEncoder):
    content_type = "application/xml"
    _tree = None
    _encoding = None

    def __init__(self, tree=None, encoding='utf-8'):
        self._tree = tree
        self._encoding = encoding

    def set_root(self, tree):
        if self._tree:
            del self._tree
        self._tree = tree

    def serialize(self):
        if isinstance(self._tree, Element):
            return ElementTree.tostring(self._tree)
        elif self._tree is None:
            raise ValueError("Tree node is None")
        schema_locations = self.get_schema_locations()
        self._tree.attrib[namespace_xsi("schemaLocation")] = " ".join("%s %s" % (uri, loc)
                                                                for uri, loc in schema_locations.items())

        return etree.tostring(self._tree, pretty_print=True, encoding=self._encoding)

    def get_schema_locations(self):
        """ Interface method. It must retrieves a dict of schema locations """
        return {}


class ImageEncoder(OWSEncoder):
    # It must to have format name. i.e "image/tiff"
    file_name = None
    data = []

    def serialize(self):
        with open(self.file_name, 'r') as f:
            data = f.read()
        return data

    def set_data(self, data):
        if self.data:
            del self.data
        self.data = data

    def _func(self, band_name, data, x, y, shared_variable):
        """
        :param data: scidbpy.SciDBArray -> It is result of scidbapy query
        :param x: int -> Width image size
        :param y: int -> Height image size
        :param shared_variable: Queue -> Shared Object
        """
        shared_variable.put((band_name, data.reshape(x, y)))

    def process_data(self, wcs, x, y, fact):
        """
        :type data: scidbpy.SciDBArray
        :type x: int
        :type y: int
        :return multiprocessing.Queue
        """
        # Default parallel mode for working with large data. It can be override by yours algorithms
        # processes = []
        queue = multiprocessing.Manager().Queue()
        # pool = multiprocessing.Pool(processes=len(wcs.attributes))
        processes = []

        for band in wcs.attributes:
            # pool.apply_async(self._func, (band, wcs.data[band], x, y * fact, queue))
            process = multiprocessing.Process(target=self._func, args=(band, wcs.data[band], x, y * fact, queue,))
            processes.append(process)
            process.start()

        self.generate_image_on_disk(wcs.geo_array, queue, x, y * fact, len(wcs.attributes))

        # Close the processes
        for process in processes:
            process.join(1)
        print("FOI")
        #
        return queue

    def generate_image_on_disk(self, metadata, data, x, y, bands_size):
        raise NotImplementedError("It must be implemented with saving file role")


class Operation(object):
    _encoder = None
    _operation_name = None

    def __init__(self, encoder_class):
        for klass in type.__subclasses__(OWSEncoder):
            if isinstance(encoder_class, klass):
                break
        else:
            raise TypeError("Invalid class type for encoder. It must be subclass of ...")
        #
        # if not issubclass(encoder_class, OWSEncoder):
        #     raise TypeError("Invalid class type for encoder. It must be subclass of ...")
        self._encoder = encoder_class

    def process(self, request):
        raise NotImplementedError("It must be implemented")

    def response(self):
        return self._encoder

class OWSDict(dict):
    _supported_services = ["wcs", "wms"]
    _supported_versions = ["2.0.0", "2.0.1", "1.3.0"]
    _supported_operations = ["getcapabilities", "describecoverage", "getcoverage", "getmap", "getfeatureinfo"]
    ogc_params = {}

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
        service = self.get('service', ' ')[0]
        # service = service if isinstance(service, basestring) else service[0]
        if service not in self._supported_services:
            raise InvalidParameterValue("Invalid service name", locator="service")
        version = self.get('version', ['2.0.1'])[0]
        if version not in self._supported_versions:
            raise InvalidParameterValue("Invalid version name", locator="version")
        request = self.get('request', ' ')[0]
        if request not in self._supported_operations:
            raise InvalidParameterValue("Invalid request name", locator="request")
        self.ogc_params['service'] = service
        self.ogc_params['version'] = version
        self.ogc_params['request'] = request

        # Remove ogc params from dict
        self.pop('service')
        if 'version' in self:
            self.pop('version')
        self.pop('request')

    def get_ows_request(self):
        req = self.ogc_params['request']
        service = self.ogc_params['service']
        return req, service if req and service else None

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