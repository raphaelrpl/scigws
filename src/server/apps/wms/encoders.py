from xml.etree import ElementTree
from apps.geo.models import GeoArray
from apps.ows.encoders import OWSEncoder
from apps.ows.utils import Identification
import psycopg2

class WMSEncoder(OWSEncoder):
    def __init__(self, params):
        self.params = params

class WMSGetCapabilitiesEnconder(WMSEncoder):
    identification = Identification()
    def encode(self, request):
        geo_arrays = GeoArray.objects.all()
        connection = psycopg2.connect(host="localhost", user="postgres", port=5433, database="modis_metadata")
        cursor = connection.cursor()
        cursor.execute("select * from geo_array")
        results = cursor.fetchall()
        ElementTree.register_namespace('wms', 'http://schemas.opengis.net/wms/1.3.0/capabilities_1_3_0.xsd')
        wms_capabilities = ElementTree.Element('WMS_Capabilities', attrib={
            'version': '1.3.0',
            'xsi:schemaLocation': 'http://www.opengis.net/wms',
            'xmlns:xlink': "http://www.w3.org/1999/xlink",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance"
        })
        service = ElementTree.SubElement(wms_capabilities, 'Service')
        ElementTree.SubElement(service, 'Name').text = 'SciWMS'
        ElementTree.SubElement(service, 'Title').text = 'Web Map Service'
        ElementTree.SubElement(service, 'Abstract').text = self.identification.data['identification']['abstract']
        keyword_list = ElementTree.SubElement(service, 'KeywordList')
        ElementTree.SubElement(keyword_list, 'Keyword').text = ''
        ElementTree.SubElement(keyword_list, 'Keyword').text = ''
        ElementTree.SubElement(keyword_list, 'OnlineResource', attrib={
            'xlink:type': 'simple',
            'xlink:href': 'http://hostname/'
        })
        contact_information = ElementTree.SubElement(service, 'ContactInformation')
        contact_person_primary = ElementTree.SubElement(contact_information, 'ContactPersonPrimary')
        ElementTree.SubElement(contact_person_primary, 'ContactPerson').text = self.identification.data['provider']['contact']['individual_name']
        ElementTree.SubElement(contact_person_primary, 'ContactOrganization').text = self.identification.data['provider']['name']
        ElementTree.SubElement(contact_information, 'ContactPosition').text = self.identification.data['provider']['contact']['position_name']
        contact_address = ElementTree.SubElement(contact_information, 'ContactAddress')
        ElementTree.SubElement(contact_address, 'AddressType').text = ''
        ElementTree.SubElement(contact_address, 'Address').text = ''
        ElementTree.SubElement(contact_address, 'City').text = ''
        ElementTree.SubElement(contact_address, 'StateOrProvince').text = ''
        ElementTree.SubElement(contact_address, 'PostCode').text = ''
        ElementTree.SubElement(contact_address, 'Country').text = ''
        ElementTree.SubElement(contact_information, 'ContactVoiceTelephone').text = ''
        ElementTree.SubElement(contact_information, 'ContactElectronicMailAddress').text = ''
        ElementTree.SubElement(service, 'Fees').text = ''
        ElementTree.SubElement(service, 'AccessConstraints').text = ''
        ElementTree.SubElement(service, 'LayerLimit').text = ''
        ElementTree.SubElement(service, 'MaxWidth').text = ''
        ElementTree.SubElement(service, 'MaxHeight').text = ''
        capability = ElementTree.SubElement(wms_capabilities, 'Capability')
        request = ElementTree.SubElement(capability, 'Request')
        get_capabilities = ElementTree.SubElement(request, 'GetCapabilities')
        ElementTree.SubElement(get_capabilities, 'Format').text = 'text/xml'
        dcp_type = ElementTree.SubElement(get_capabilities, 'DCPType')
        http = ElementTree.SubElement(dcp_type, 'HTTP')
        get = ElementTree.SubElement(http, 'Get')
        ElementTree.SubElement(get, 'OnlineResource', attrib={
            'xlink:type': 'simple',
            'xlink:href': 'http://hostname/'
        })
        post = ElementTree.SubElement(http, 'Post')
        ElementTree.SubElement(post, 'OnlineResource', attrib={
            'xlink:type': 'simple',
            'xlink:href': 'http://hostname/'
        })
        get_map = ElementTree.SubElement(request, 'GetMap')
        ElementTree.SubElement(get_map, 'Format').text = 'image/gif'
        ElementTree.SubElement(get_map, 'Format').text = 'image/png'
        ElementTree.SubElement(get_map, 'Format').text = 'image/jpeg'
        dcp_type = ElementTree.SubElement(get_map, 'DCPType')
        http = ElementTree.SubElement(dcp_type, 'HTTP')
        get = ElementTree.SubElement(http, 'Get')
        ElementTree.SubElement(get, 'OnlineResource', attrib={
            'xlink:type': 'simple',
            'xlink:href': 'http://hostname/'
        })
        get_feature_info = ElementTree.SubElement(request, 'GetFeatureInfo')
        ElementTree.SubElement(get_feature_info, 'Format').text = 'text/xml'
        dcp_type = ElementTree.SubElement(get_feature_info, 'DCPType')
        http = ElementTree.SubElement(dcp_type, 'HTTP')
        get = ElementTree.SubElement(http, 'Get')
        ElementTree.SubElement(get, 'OnlineResource', attrib={
            'xlink:type': 'simple',
            'xlink:href': 'http://hostname/'
        })
        exception = ElementTree.SubElement(capability, 'Exception')
        ElementTree.SubElement(exception, 'Format').text = 'text/xml'
        layer = ElementTree.SubElement(capability, 'Layer')
        ElementTree.SubElement(layer, 'Title').text = 'Web Map Service'
        ElementTree.SubElement(layer, 'CRS').text = '%s' % geo_arrays[0].crs
        authority_url = ElementTree.SubElement(layer, 'AuthorityURL', attrib={'name': 'DIF_ID'})
        ElementTree.SubElement(authority_url, 'OnlineResource', attrib={
            'xlink:type': 'simple',
            'xlink:href': '%s' % (results[0][3])
        })
        for geo in geo_arrays:
            layeri = ElementTree.SubElement(layer, 'Layer')
            ElementTree.SubElement(layeri, 'Name').text = "%s" % geo.name
            ElementTree.SubElement(layeri, 'Title').text = "%s" % geo.description
            ElementTree.SubElement(layeri, 'CRS').text = "%s" % geo.crs
            ElementTree.SubElement(layeri, 'BoundingBox', attrib={
                'CRS': '',
                'minx': '%s' % geo.x_min,
                'miny': '%s' % geo.y_min,
                'maxx': '%s' % geo.x_max,
                'maxy': '%s' % geo.y_max,
                'resx': '%s' % geo.x_resolution,
                'resy': '%s' % geo.y_resolution
            })
        cursor.close()
        connection.close()
        return wms_capabilities