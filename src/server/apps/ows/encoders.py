from base import XMLEncoder
from utils import namespace_xlink, OWS_MAKER


class OWSEncoder(XMLEncoder):
    def encode_reference(self, node_name, href, reftype="simple"):
        attributes = {namespace_xlink("href"): href}
        if reftype:
            attributes[namespace_xlink("type")] = reftype

        return OWS_MAKER(node_name, **attributes)


class OWSExceptionResponse(XMLEncoder):
    def dispatch(self, message, version, code, locator=None):
        exception_attributes = {"exceptionCode": str(code)}

        if locator:
            exception_attributes["locator"] = str(locator)

        exception_text = (OWS_MAKER("ExceptionText", message),) if message else ()

        return OWS_MAKER(
            "ExceptionReport",
            OWS_MAKER("Exception",
                      *exception_text, **exception_attributes), version=version, **{namespace_xlink("lang"): "en"}
        )