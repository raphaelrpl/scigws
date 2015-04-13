class OWSException(Exception):
    """ Base Exception """
    code = None
    locator = None

    def __init__(self, msg, locator=None):
        super(OWSException, self).__init__(msg)
        self.locator = locator


class OWSIOError(OWSException):
    """ I/O operation failed. """
    pass


class InvalidParameterValue(OWSException):
    code = "InvalidParameterValue"


class MissingParameterValue(OWSException):
    code = "MissingParameterValue"