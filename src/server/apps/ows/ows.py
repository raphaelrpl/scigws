from xml.etree import ElementTree
from exception import OWSException
from utils import Identification, OWS_MAKER
from encoders import encode_reference


class OWSMeta(object):
    """ OWS metadata for Web Coverage Service 2.0 or...."""
    identification = None
    supported_services = ["wcs", "wms"]
    ows = "ows"

    def __init__(self, url="http://127.0.0.1:8000/ows?"):
        self.meta = Identification()
        identification = self.meta.data.get('identification', {})
        provider = self.meta.data.get('provider', {})
        profiles = self.meta.data.get('profiles', [])
        self.formats = self.meta.data.get('formats', [])
        contact = provider.get('contact', {})

        self.root_identification = OWS_MAKER(
            "ServiceIdentification",
            OWS_MAKER("Title", identification.get('title')),
            OWS_MAKER("Abstract", identification.get('abstract')),
            OWS_MAKER("ServiceType", identification.get('service_type')),
            OWS_MAKER("ServiceTypeVersion", identification.get('service_type_version')),
            OWS_MAKER("Profile", "http://www.opengis.net/spec/WCS_protocol-binding_s"),
            OWS_MAKER("Profile", "http://www.opengis.net/spec/WCS_protocol-binding_get-kvp/1.0/conf/get-kvp"),
            OWS_MAKER("Profile", "http://www.opengis.net/spec/WCS_geotiff-coverages/1.0/conf/geotiff-coverage"),
        )

        self.root_provider = OWS_MAKER(
            "ServiceProvider",
            OWS_MAKER("ProviderName", provider.get('name')),
            OWS_MAKER("ProviderSite", provider.get('site')),
            OWS_MAKER(
                "Contact",
                OWS_MAKER(
                    "IndividualName", contact.get('individual_name')),
                OWS_MAKER(
                    "PositionName", contact.get('position_name')),
                OWS_MAKER(
                    "ContactInfo",
                    OWS_MAKER(
                        "Phone",
                        OWS_MAKER("Voice", contact.get('contact_info', {}).get("phone", {}).get('voice'))),
                    OWS_MAKER(
                        "Address",
                        OWS_MAKER(
                            "DeliveryPoint", contact.get('contact_info', {}).get('address', {}).get('delivery_point')),
                        OWS_MAKER(
                            "City", contact.get('contact_info', {}).get('address', {}).get('city')),
                        OWS_MAKER(
                            "Country", contact.get('contact_info', {}).get('address', {}).get('country')),
                        OWS_MAKER(
                            "PostalCode", contact.get('contact_info', {}).get('address', {}).get('postal_code')),
                        OWS_MAKER(
                            "ElectronicMailAddress",
                            contact.get('contact_info', {}).get('address', {}).get("mail_address")))))
        )

        self.root_operations = OWS_MAKER(
            "OperationsMetadata",
            OWS_MAKER("Operation",
                      OWS_MAKER("DCP",
                                OWS_MAKER("HTTP", encode_reference("Get", url)),
                                OWS_MAKER("HTTP", encode_reference("Post", url)),
                                ), name="GetCapabilities")
        )