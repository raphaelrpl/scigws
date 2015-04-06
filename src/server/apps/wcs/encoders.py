from apps.ows.encoders import OWSEncoder
from apps.ows.utils import OWS_MAKER
from apps.ows.ows import OWSMeta
from utils import WCS_MAKER, wcs_set


class GetCapabilitiesEncoder(OWSEncoder):
    def get_schema_locations(self):
        return wcs_set.schema_locations

    def encode(self, url="http://127.0.0.1:8000/ows?"):
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

        contact = ows.provider.get('contact')
        root_provider = OWS_MAKER(
            "ServiceProvider",
            OWS_MAKER("ProviderName", ows.provider.get('name')),
            OWS_MAKER("ProviderSite", ows.provider.get('site')),
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

        nodes.append(root_provider)

        root_operations = OWS_MAKER(
            "OperationsMetadata",
            OWS_MAKER("Operation",
                      OWS_MAKER("DCP",
                                OWS_MAKER("HTTP", self.encode_reference("Get", url)),
                                OWS_MAKER("HTTP", self.encode_reference("Post", url)),
                                ), name="GetCapabilities")
        )

        nodes.append(root_operations)

        root_service_metadata = WCS_MAKER("ServiceMetadata")
        formats = [WCS_MAKER("formatSupported", f.get('name')) for f in ows.formats]
        root_service_metadata.extend(formats)

        nodes.append(root_service_metadata)

        contents = WCS_MAKER(
            "Contents",
            WCS_MAKER(

            )
        )

        root = WCS_MAKER("Capabilities", *nodes, version="2.0.1")
        return root