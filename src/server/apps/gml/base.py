from lxml.etree import tostring, ElementBase
from utils import namespace_gml


class GMLBase(ElementBase):
    TAG = None

    def __init__(self, *children, **attributes):
        self.attributes = attributes
        self.TAG = '{' + namespace_gml.uri + '}' + self.TAG
        super(GMLBase, self).__init__(*children, attrib=attributes, nsmap={'gml': namespace_gml.uri})

    def to_xml(self, encoding="UTF-8"):
        return tostring(self, pretty_print=True, encoding=encoding)


class GMLRangeBase(GMLBase):
    TAG = "RangeBase"

    def __init__(self, limits, *children, **attributes):
        super(GMLRangeBase, self).__init__(*children, **attributes)
        self.text = (" %s" * len(limits)).lstrip(' ')