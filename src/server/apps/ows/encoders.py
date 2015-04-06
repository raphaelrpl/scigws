from base import XMLEncoder
from utils import namespace_xlink, OWS_MAKER


class OWSEncoder(XMLEncoder):
    def encode_reference(self, node_name, href, reftype="simple"):
        attributes = {namespace_xlink("href"): href}
        if reftype:
            attributes[namespace_xlink("type")] = reftype

        return OWS_MAKER(node_name, **attributes)