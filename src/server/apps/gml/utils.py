from apps.ows.utils import Namespace, NamespaceSet
from lxml.builder import ElementMaker


namespace_gml = Namespace("http://www.opengis.net/gml/3.2", "gml")
namespace_gmlcov = Namespace("http://www.opengis.net/gmlcov/1.0", "gmlcov")

namespace_set = NamespaceSet(namespace_gml, namespace_gmlcov)


GML = ElementMaker(namespace=namespace_gml.uri, nsmap=namespace_set)
GMLCOV = ElementMaker(namespace=namespace_gmlcov.uri, nsmap=namespace_set)