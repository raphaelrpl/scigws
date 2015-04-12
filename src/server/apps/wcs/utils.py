from xml.etree import ElementTree
from xml.dom.minidom import parseString
from apps.ows.utils import Namespace, NamespaceSet
from lxml.builder import ElementMaker
from apps.gml.utils import namespace_gmlcov, namespace_gml


namespace_wcs = Namespace("http://www.opengis.net/wcs/2.0", "wcs")
namespace_swe = Namespace("http://www.opengis.net/swe/2.0", "swe")
namespace_ows = Namespace("http://www.opengis.net/ows/2.0", "ows")
namespace_wcseo = Namespace("http://www.opengis.net/wcseo/1.0", "wcseo",
                            "http://schemas.opengis.net/wcs/wcseo/1.0/wcsEOAll.xsd")

wcs_set = NamespaceSet(namespace_wcs, namespace_swe, namespace_ows, namespace_gml, namespace_gmlcov, namespace_wcseo)

WCS_MAKER = ElementMaker(namespace=namespace_wcs.uri, nsmap=wcs_set)

WCSEO_MAKER = ElementMaker(namespace=namespace_wcseo.uri, nsmap=wcs_set)


def pretty_xml(element):
    xml_string = ElementTree.tostring(element)
    to_parse = parseString(xml_string)
    return to_parse.toprettyxml()