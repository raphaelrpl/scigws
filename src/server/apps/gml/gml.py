from xml.etree import ElementTree
from exception import GMLException
from apps.geo.models import GeoArrayTimeLine
from base import GMLRangeBase, GMLBase


class GMLLowerCorner(GMLRangeBase):
    def __init__(self, limits, **attributes):
        """ It defines a GMLLowerCorner node based in WCS 2.0 """
        super(GMLLowerCorner, self).__init__("lowerCorner", limits, **attributes)


class GMLUpperCorner(GMLRangeBase):
    def __init__(self, limits, **attributes):
        """ It defines a GMLUpperCorner node based in WCS 2.0 """
        super(GMLUpperCorner, self).__init__("upperCorner", limits, **attributes)


class GMLEnvelope(GMLBase):
    def __init__(self, data, **attributes):
        super(GMLEnvelope, self).__init__(**attributes)
        self.node_name = "Envelope"
        self.attributes = attributes
        self.data = data
        self.lower = GMLLowerCorner(data.get('min'))
        self.upper = GMLLowerCorner(data.get('max'))
        nodes = [self.lower.root, self.upper.root]
        self.root = self.maker(self.node_name, **attributes)
        self.root.extend(nodes)


class GMLBoundedBy(GMLBase):
    envelope = None

    def __init__(self, data, **attributes):
        super(GMLBoundedBy, self).__init__(**attributes)
        self.node_name = "boundedBy"

        self.envelope = GMLEnvelope(data)

        self.root = self.maker(self.node_name, self.envelope.root, **attributes)


class GMLMeta(object):
    def __init__(self, identifier, meta, times):
        self.identifier = identifier
        if meta is None:
            raise GMLException("Metadata for \"identifier\" is none. <{0}>".format(meta))
        self.meta = meta
        self.times = times

    def get_axis_labels(self):
        output = "{0} {1} {2}".format(self.meta.get('x_dim_name'),
                                      self.meta.get('y_dim_name'),
                                      self.meta.get('t_dim_name'))
        return output

    def get_envelope_values(self):
        if self.times:
            low = "%s %s %s" % (self.meta.get('x_min'), self.meta.get('y_min'), self.times[0].time_point)
            high = "%s %s %s" % (self.meta.get('x_max'), self.meta.get('y_max'), GeoArrayTimeLine.objects.filter(array__name=self.identifier).last().time_point)
            return low, high
        return "", ""

    def get_bounded_by(self):
        ElementTree.register_namespace("gml", "http://www.opengis.net/gml/3.2")
        bounded_by = ElementTree.Element("gml:boundedBy")
        envelope = ElementTree.SubElement(bounded_by, "gml:Envelope", attrib={
            "axisLabels": self.get_axis_labels(),
            "srsDimension": str(len(self.get_axis_labels().split(" "))),
            "srsName": "http://www.opengis.net/def/crs/EPSG/0/4326"
        })
        envelope_values = self.get_envelope_values()

        lower = ElementTree.SubElement(envelope, "gml:lowerCorner")
        lower.text = envelope_values[0]
        upper = ElementTree.SubElement(envelope, "gml:upperCorner")
        upper.text = envelope_values[1]

        return bounded_by

    def get_grid(self):
        grid = ElementTree.Element("gml:Grid", attrib={
            "dimension": str(len(self.get_axis_labels().split(" ")))})
        limits = ElementTree.SubElement(grid, "gml:limits")
        envelope = ElementTree.SubElement(limits, "gml:GridEnvelope")
        envelope_values = self.get_envelope_values()
        low = ElementTree.SubElement(envelope, "gml:low")
        low.text = envelope_values[0]
        high = ElementTree.SubElement(envelope, "gml:high")
        high.text = envelope_values[1]

        return grid