from xml.etree import ElementTree


def throws_exception(params):
    namespace = {"ows": "http://www.opengis.net/ows/2.0"}
    ElementTree.register_namespace("ows", "http://www.opengis.net/ows/2.0")
    root = ElementTree.Element("{%s}ExceptionReport" % namespace['ows'], attrib={
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "version": "2.0.1",
        "xsi:schemaLocation": "http://www.opengis.net/ows/2.0 http://schemas.opengis.net/ows/2.0/owsExceptionReport.xsd"
    })
    exception = ElementTree.SubElement(root, "ows:Exception", exceptionCode=params.get("exceptionCode", ""),
                                       locator=params.get("locator", ""))
    exception_text = ElementTree.SubElement(exception, "ows:ExceptionText")
    exception_text.text = "WCS server error. %s \"%s\"" % (params.get("message", ""), params.get("param", ""))
    return ElementTree.tostring(root)


class WCSException(Exception):
    def __init__(self, msg):
        super(WCSException, self).__init__(msg)
        self.msg = msg