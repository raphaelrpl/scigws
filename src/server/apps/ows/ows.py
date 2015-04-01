from xml.etree import ElementTree
from exception import OWSException, OWSIOError

import os
import json


class Metadata(object):
    """ OWS metadata for Web Coverage Service 2.0 or...."""
    root_identification = None
    root_provider = None
    root_operations = None
    config = None
    prefix = False
    service = None
    supported_services = ["wcs", "wms"]
    ows = "ows"

    def __init__(self, prefix=True, service="wcs", path=None, name="metadata.json"):
        if service not in self.supported_services:
            raise OWSException("Invalid service name: %s" % service)
        self.service = service

        # SET DEFAULT PATH IF THERE IS NOT
        if path is None:
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        try:
            with open(os.path.join(path, name)) as data:
                self.config = json.loads(data.read())
        except IOError as e:
            raise OWSIOError(e)
        except StandardError as e:
            raise OWSException(e)

        if prefix:
            self.root_identification = ElementTree.Element("%s:%s" % (self.ows, "ServiceIdentification"))
            title = ElementTree.SubElement(self.root_identification, "%s:%s" % (self.ows, "Title"))
            abstract = ElementTree.SubElement(self.root_identification, "%s:%s" % (self.ows, "Abstract"))
            service_type = ElementTree.SubElement(self.root_identification, "%s:%s" % (self.ows, "ServiceType"))
            service_version = ElementTree.SubElement(self.root_identification, "%s:%s" % (self.ows, "ServiceTypeVersion"))

            self.root_provider = ElementTree.Element("%s:%s" % (self.ows, "ServiceProvider"))
            name = ElementTree.SubElement(self.root_provider, "%s:%s" % (self.ows, "ProviderName"))
            site = ElementTree.SubElement(self.root_provider, "%s:%s" % (self.ows, "ProviderSite"))
            contact = ElementTree.SubElement(self.root_provider, "%s:%s" % (self.ows, "ServiceContact"))
            individual_name = ElementTree.SubElement(contact, "%s:%s" % (self.ows, "IndividualName"))
            position_name = ElementTree.SubElement(contact, "%s:%s" % (self.ows, "PositionName"))
            contact_info = ElementTree.SubElement(contact, "%s:%s" % (self.ows, "ContactInfo"))
            phone = ElementTree.SubElement(contact_info, "%s:%s" % (self.ows, "Phone"))
            address = ElementTree.SubElement(contact_info, "%s:%s" % (self.ows, "Address"))
            delivery_point = ElementTree.SubElement(address, "%s:%s" % (self.ows, "DeliveryPoint"))
            city = ElementTree.SubElement(address, "%s:%s" % (self.ows, "City"))
            country = ElementTree.SubElement(address, "%s:%s" % (self.ows, "Country"))
            postal_code = ElementTree.SubElement(address, "%s:%s" % (self.ows, "PostalCode"))
            mail_address = ElementTree.SubElement(address, "%s:%s" % (self.ows, "ElectronicMailAddress"))
        else:
            # EXAMPLE
            self.root_identification = ElementTree.Element("%s" % "Service", )
            title = ElementTree.SubElement(self.root_identification, "%s" % "Title")
            abstract = ElementTree.SubElement(self.root_identification, "%s" % "Abstract")
            service_type = ElementTree.SubElement(self.root_identification, "%s" % "ServiceType")
            service_version = ElementTree.SubElement(self.root_identification, "%s" % "ServiceTypeVersion")

            self.root_provider = ElementTree.Element("%s" % self.ows, "ServiceProvider")
            name = ElementTree.SubElement(self.root_provider, "%s" % self.ows, "ProviderName")
            site = ElementTree.SubElement(self.root_provider, "%s" % self.ows, "ProviderSite")
            contact = ElementTree.SubElement(self.root_provider, "%s" % self.ows, "ServiceContact")
            individual_name = ElementTree.SubElement(contact, "%s" % "IndividualName")
            position_name = ElementTree.SubElement(contact, "%s" % "PositionName")
            contact_info = ElementTree.SubElement(contact, "%s" % "ContactInfo")
            phone = ElementTree.SubElement(contact_info, "%s" % "Phone")
            address = ElementTree.SubElement(contact_info, "%s" % "Address")
            delivery_point = ElementTree.SubElement(address, "%s" % "DeliveryPoint")
            city = ElementTree.SubElement(address, "%s" % "City")
            country = ElementTree.SubElement(address, "%s" % "Country")
            postal_code = ElementTree.SubElement(address, "%s" % "PostalCode")
            mail_address = ElementTree.SubElement(address, "%s" % "ElectronicMailAddress")

        title.text = self.config['identification'].get('title', '')
        abstract.text = self.config['identification'].get('abstract', '')
        service_type.text = self.config['identification'].get('service_type', '')
        service_version.text = self.config['identification'].get('service_type_version', '')
        name.text = self.config['provider'].get('name', '')
        site.attrib['xlink:href'] = self.config['provider'].get('site', '')
        individual_name.text = self.config['provider']['contact'].get('individual_name', '')
        position_name.text = self.config['provider']['contact'].get('position_name', '')
        phone.text = self.config['provider']['contact']['contact_info']['phone'].get('voice', '')
        delivery_point.text = self.config['provider']['contact']['contact_info']['address'].get('delivery_point', '')
        city.text = self.config['provider']['contact']['contact_info']['address'].get('city', '')
        country.text = self.config['provider']['contact']['contact_info']['address'].get('country', '')
        postal_code.text = self.config['provider']['contact']['contact_info']['address'].get('postal_code', '')
        mail_address.text = self.config['provider']['contact']['contact_info']['address'].get('mail_address', '')

        self.prefix = prefix
        del path, service, title, abstract, service_type, service_version, name, site, contact, mail_address, \
            individual_name, position_name, phone, delivery_point, city, country

    def generate_profiles(self):
        """ Generate profiles in ows:ServiceIdentification for WCS 2.0, it reads from metadata file """
        if self.root_identification is None:
            raise OWSException(ElementTree.Element("%s:%s" % (self.ows, "ServiceIdentification")))
        if self.config is None:
            raise OWSException("Cannot find Metadata file node, it is must be initialized")
        profiles = self.config.get('profiles', None)
        if profiles and self.prefix:
            for profile in profiles:
                temp = ElementTree.SubElement(self.root_identification, "ows:Profile")
                temp.text = profile.get('name')
                del temp

    def generate_operations(self, url):
        """ Generate operations in ows:OperationsMetadata for WCS 2.0"""
        if self.prefix:
            if self.root_operations is None:
                self.root_operations = ElementTree.Element("%s:%s" % (self.ows, "OperationsMetadata"))
            operations = [
                ElementTree.SubElement(self.root_operations, "%s:%s" % (self.ows, "Operation"), attrib={
                    "name": "GetCapabilities"}),
                ElementTree.SubElement(self.root_operations, "%s:%s" % (self.ows, "Operation"), attrib={
                    "name": "DescribeCoverage"}),
                ElementTree.SubElement(self.root_operations, "%s:%s" % (self.ows, "Operation"), attrib={
                    "name": "GetCoverage"})
            ]
            for operation in operations:
                dcp = ElementTree.SubElement(operation, "ows:DCP")
                http = ElementTree.SubElement(dcp, "ows:HTTP")
                ElementTree.SubElement(http, "ows:Get", attrib={
                    "xlink:type": "simple",
                    "xlink:href": url
                })