from utils import GML_MAKER
from lxml.etree import tostring


class GMLBase(object):
    node_name = None
    root = None
    maker = GML_MAKER

    def __init__(self, **attributes):
        self.attributes = attributes

    def get_root(self):
        return self.root

    def to_xml(self, encoding="UTF-8"):
        return tostring(self.root, pretty_print=True, encoding=encoding)


class GMLRangeBase(GMLBase):
    def __init__(self, node_name, limits, **attributes):
        super(GMLRangeBase, self).__init__(**attributes)
        self.node_name = node_name
        string_limits = (" %s" * len(limits)).lstrip(' ')
        self.root = self.maker(self.node_name, string_limits % tuple(limits), **attributes)