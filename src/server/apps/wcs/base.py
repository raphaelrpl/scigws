from xml.etree import ElementTree
from exception import WCSException
from json import loads
from psycopg2 import connect

import abc


class WCSBase(object):
    __metaclass__ = abc.ABCMeta
    geo_arrays = None

    def __init__(self, db_path="config/db.config.json", meta="config/geo_arrays.json"):
        super(WCSBase, self).__init__()
        self.ns_dict = self._initialize_namespaces()
        self.dom = self._create_dom()
        self._register_namespaces()
        try:
            with open(meta) as data:
                self.geo_arrays = loads(data.read())
            with open(db_path) as data:
                self.config = loads(data.read())
        except StandardError as e:
            raise WCSException(e)

    @classmethod
    def _initialize_namespaces(cls):
        return {
            "gml": "http://www.opengis.net/gml/3.2",
            "gmlcov": "http://www.opengis.net/gmlcov/1.0",
            "swe": "http://www.opengis.net/swe/2.0",
            "ows": "http://www.opengis.net/ows/2.0",
            "wcs": "http://www.opengis.net/wcs/2.0"
        }

    @abc.abstractmethod
    def _create_dom(self):
        """
        :return:
        """""

    def _register_namespaces(self):
        for namespace in self.ns_dict:
            ElementTree.register_namespace(namespace, self.ns_dict[namespace])