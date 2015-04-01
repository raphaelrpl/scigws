from xml.etree import ElementTree
from xml.dom.minidom import parseString
from django.core import validators


def pretty_xml(element):
    xml_string = ElementTree.tostring(element)
    to_parse = parseString(xml_string)
    return to_parse.toprettyxml(encoding='UTF-8')