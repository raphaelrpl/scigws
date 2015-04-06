from apps.ows.encoders import OWSEncoder
from apps.ows.utils import OWS_MAKER
from apps.ows.ows import OWSMeta
from utils import WCS_MAKER
from django.contrib.sites.models import Site


class GetCapabilitiesEncoder(OWSEncoder):
    def encode(self):
        nodes = []
        ows = OWSMeta()
        root_identification = OWS_MAKER(
            "ServiceIdentification",
            OWS_MAKER("Title", ows.identification.get('title')),
            OWS_MAKER("Abstract", ows.identification.get('abstract')),
            OWS_MAKER("ServiceType", ows.identification.get('service_type')),
            OWS_MAKER("ServiceTypeVersion", ows.identification.get('service_type_version')),
            OWS_MAKER("Profile", "http://www.opengis.net/spec/WCS_protocol-binding_s"),
            OWS_MAKER("Profile", "http://www.opengis.net/spec/WCS_protocol-binding_get-kvp/1.0/conf/get-kvp"),
            OWS_MAKER("Profile", "http://www.opengis.net/spec/WCS_geotiff-coverages/1.0/conf/geotiff-coverage"),
        )
        nodes.append(root_identification)

        contac = ows.provider.get('contact')
        root_provider = OWS_MAKER(
            "ServiceProvider",
            OWS_MAKER("ProviderName", ows.provider.get('name')),
            OWS_MAKER("ProviderSite", ows.provider.get('site')),
            OWS_MAKER("Contact",
                      OWS_MAKER("IndividualName", contac.get('individual_name')),
                      OWS_MAKER("PositionName", contac.get('position_name')),
                      OWS_MAKER("ContactInfo",
                                OWS_MAKER("Phone",
                                          OWS_MAKER("Voice", contac.get('contact_info', {}).get("phone", {}).get('voice'))),
                                OWS_MAKER("Address",
                                          OWS_MAKER("DeliveryPoint", contac.get('contact_info', {}).get('address', {}).get('delivery_point')),
                                          OWS_MAKER("City", contac.get('contact_info', {}).get('address', {}).get('city')),
                                          OWS_MAKER("Country", contac.get('contact_info', {}).get('address', {}).get('country')),
                                          OWS_MAKER("PostalCode", contac.get('contact_info', {}).get('address', {}).get('postal_code')),
                                          OWS_MAKER("ElectronicMailAddress", contac.get('contact_info', {}).get('address', {}).get("mail_address")))))
        )

        nodes.append(root_provider)

        domain = Site.objects.get_current()
        print(domain)

        root_operations = OWS_MAKER(
            "OperationsMetadata",
            OWS_MAKER("Operation",
                      OWS_MAKER("DCP",
                                OWS_MAKER("HTTP", self.encode_reference("Get", "a")),
                                OWS_MAKER("HTTP", self.encode_reference("Post", "a")),
                                ), name="GetCapabilities")
        )

        nodes.append(root_operations)

        root_service_metadata = WCS_MAKER("ServiceMetadata")
        for format_supported in ows.formats:
            root_service_metadata.extend(WCS_MAKER("formatSupported", format_supported.get('name')))

        root = WCS_MAKER("Capabilities", *nodes, version="2.0.1")
        return root