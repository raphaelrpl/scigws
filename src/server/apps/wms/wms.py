#
# Copyright (C) 2014-2015 National Institute For Space Research (INPE) - Brazil.
#
# This file is part of the SciWMS.
#
# SciWMS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# SciWMS is distributed  "AS-IS" in the hope that it will be useful,
# but WITHOUT ANY WARRANTY OF ANY KIND; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with SciWMS. See COPYING. If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
#

from xml.etree import ElementTree
import psycopg2


class WMS():
    root = None

    def capabilities(self):
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
        ElementTree.SubElement(service, 'Name').text = 'WMS'
        ElementTree.SubElement(service, 'Title').text = 'Web Map Service'
        ElementTree.SubElement(service, 'Abstract').text = ''
        keyword_list = ElementTree.SubElement(service, 'KeywordList')
        ElementTree.SubElement(keyword_list, 'Keyword').text = ''
        ElementTree.SubElement(keyword_list, 'Keyword').text = ''
        ElementTree.SubElement(keyword_list, 'OnlineResource', attrib={
            'xlink:type': 'simple',
            'xlink:href': 'http://hostname/'
        })
        contact_information = ElementTree.SubElement(service, 'ContactInformation')
        contact_person_primary = ElementTree.SubElement(contact_information, 'ContactPersonPrimary')
        ElementTree.SubElement(contact_person_primary, 'ContactPerson').text = ''
        ElementTree.SubElement(contact_person_primary, 'ContactOrganization').text = ''
        ElementTree.SubElement(contact_information, 'ContactPosition').text = ''
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
        ElementTree.SubElement(layer, 'CRS').text = '%s' % (results[0][4])
        authority_url = ElementTree.SubElement(layer, 'AuthorityURL', attrib={'name': 'DIF_ID'})
        ElementTree.SubElement(authority_url, 'OnlineResource', attrib={
            'xlink:type': 'simple',
            'xlink:href': '%s' % (results[0][3])
        })
        layer = ElementTree.SubElement(layer, 'Layer')
        ElementTree.SubElement(layer, 'Name').text = "%s" % (results[0][1])
        ElementTree.SubElement(layer, 'Title').text = "%s" % (results[0][2])
        ElementTree.SubElement(layer, 'CRS').text = "%s" % (results[0][4])
        ElementTree.SubElement(layer, 'BoundingBox', attrib={
            'CRS': '',
            'minx': '%s' % (results[0][6]),
            'miny': '%s' % (results[0][10]),
            'maxx': '%s' % (results[0][7]),
            'maxy': '%s' % (results[0][11]),
            'resx': '%s' % (results[0][8]),
            'resy': '%s' % (results[0][12])
        })
        cursor.close()
        connection.close()
        return ElementTree.tostring(wms_capabilities)

    def map(self):
        return

    def feature_info(self):
        return