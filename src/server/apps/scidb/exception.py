class SciDBException(Exception):
    pass


class SciDBQueryError(SciDBException):
    pass


class SciDBConnectionError(SciDBException):
    pass