from xml.etree import ElementTree
from exception import OWSException
from utils import Identification, OWS_MAKER


class OWSMeta(object):
    """ OWS metadata for Web Coverage Service 2.0 or...."""
    identification = None
    supported_services = ["wcs", "wms"]
    ows = "ows"

    def __init__(self):
        self.meta = Identification()
        self.identification = self.meta.data.get('identification', {})
        self.provider = self.meta.data.get('provider', {})
        self.profiles = self.meta.data.get('profiles', [])
        self.formats = self.meta.data.get('formats', [])