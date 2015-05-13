from exception import OWSIOError
from json import loads
from lxml.builder import ElementMaker


class Namespace(object):
    def __init__(self, uri, prefix=None, schema_location=None):
        self._uri = uri
        self._namespace_uri = "{%s}" % uri
        self._prefix = prefix
        self._schema_location = schema_location

    def __call__(self, tag):
        return self._namespace_uri + tag

    def __str__(self):
        return "<Namespace: %s - %s>" % (self._prefix, self._uri)

    @property
    def uri(self):
        return self._uri

    @property
    def prefix(self):
        return self._prefix

    @property
    def schema_location(self):
        return self._schema_location


class NamespaceSet(dict):
    def __init__(self, *namespaces):
        super(NamespaceSet, self).__init__()
        self._schema_location_set = {}
        for namespace in namespaces:
            self.add(namespace)

    @property
    def schema_locations(self):
        return self._schema_location_set

    def add(self, namespace):
        self[namespace.prefix] = namespace.uri
        if namespace.schema_location:
            self._schema_location_set[namespace.uri] = namespace.schema_location


namespace_ows = Namespace("http://www.opengis.net/ows/2.0", "ows")
namespace_xsi = Namespace("http://www.w3.org/2001/XMLSchema-instance", "xsi")
namespace_set = NamespaceSet(namespace_ows)
namespace_xlink = Namespace("http://www.w3.org/1999/xlink", "xlink")

OWS_MAKER = ElementMaker(namespace=namespace_ows.uri, nsmap=namespace_set)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args)
        return cls._instances[cls]


class Meta(object):
    data = None
    __metaclass__ = Singleton

    def __init__(self, path):
        try:
            with open(path) as f:
                self.data = loads(f.read())
        except IOError as e:
            raise OWSIOError(e)


class Identification(Meta):
    def __init__(self, path="config/metadata.json"):
        super(Identification, self).__init__(path)


class DBConfig(Meta):
    scidb = {}

    def __init__(self, path="config/db.config.json"):
        super(DBConfig, self).__init__(path)
        self.scidb = self.data.get('scidb')

    def get_scidb_credentials(self):
        return self.scidb


class GeoArray(Meta):
    def __init__(self, path="config/db.config.json"):
        super(GeoArray, self).__init__(path)