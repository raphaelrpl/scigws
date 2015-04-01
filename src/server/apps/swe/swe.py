from xml.etree import ElementTree
from exception import SWEException, SWEIOError

import os
import json


class SWEMeta(object):
    _services_supported = ['wcs']

    def __init__(self, identifier, meta):
        if not meta:
            raise SWEException("Metadata for \"identifier\" is none. <{0}>".format(meta))
        self.identifier = identifier
        self.meta = meta

    def get_data_record(self):
        """
        Get fields based SWE Specification
        :return: root node with all children nodes
        """
        ElementTree.register_namespace("swe", "http://www.opengis.net/swe/2.0")
        data_record = ElementTree.Element("swe:%s" % "DataRecord")
        if self.identifier not in self.meta.get('name'):
            raise SWEException("Cannot find coverage \"%s\"." % self.identifier)
        if self.meta.get('attributes') is None:
            raise SWEException("Cannot find attributes of \"%s\"." % self.identifier)
        for attr in self.meta.get('attributes'):
            field = ElementTree.SubElement(data_record, "swe:field", attrib={'name': attr['name']})
            quantity = ElementTree.SubElement(field, "swe:Quantity", attrib={})
            # ElementTree.SubElement(quantity, "swe:label").text = attr['label']
            ElementTree.SubElement(quantity, "swe:description").text = attr['description']
            # FIXME: Figure out a sort of uom
            ElementTree.SubElement(quantity, "swe:uom").text = "NVDI"
            constraint = ElementTree.SubElement(quantity, "swe:constraint")
            allowed_values = ElementTree.SubElement(constraint, "swe:AllowedValues")
            ElementTree.SubElement(allowed_values, "swe:interval").text = "%s %s" % (
                attr['range_min'],
                attr['range_max'])

        return data_record