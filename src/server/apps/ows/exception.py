class OWSException(Exception):
    """ Base Exception """
    code = None
    locator = None
    version = None

    def __init__(self, msg, locator=None, version=None):
        super(OWSException, self).__init__(msg)
        self.locator = locator
        self.version = version


class OWSIOError(OWSException):
    """ I/O operation failed. """
    pass


class InvalidParameterValue(OWSException):
    code = "InvalidParameterValue"


class MissingParameterValue(OWSException):
    code = "MissingParameterValue"