from lxml import etree
from utils import namespace_xsi


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