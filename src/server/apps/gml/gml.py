from xml.etree import ElementTree
from exception import GMLException


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
            low = "%s %s %s" % (self.meta.get('x_min'), self.meta.get('y_min'), self.times[0][1])
            high = "%s %s %s" % (self.meta.get('x_max'), self.meta.get('y_max'), self.times[-1][1])
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