class OWSException(Exception):
    """ Base Exception """
    pass


class OWSIOError(OWSException):
    """ I/O operation failed. """
    pass