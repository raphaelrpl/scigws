class WCSException(Exception):
    """ Base Exception """
    code = None
    locator = None
    version = None

    def __init__(self, msg, locator=None, version="2.0.1"):
        super(WCSException, self).__init__(msg)
        self.locator = locator
        self.version = version


class LocatorListException(Exception):
    code = None

    def __init__(self, *errors_list):
        self.errors = errors_list


class NoSuchCoverageException(WCSException):
    code = "NoSuchCoverageException"

    def __init__(self, msg="Invalid coverage identifier", locator="coverageID"):
        super(NoSuchCoverageException, self).__init__(msg, locator)


class InvalidSubset(WCSException):
    code = "InvalidSubsetting"
    locator = "subset"

    def __init__(self, msg="Invalid subset", locator="subset"):
        super(InvalidSubset, self).__init__(msg, locator)


class InvalidRangeSubSet(WCSException):
    code = "InvalidRangeSubset"

    def __init__(self, msg="Invalid RangeSubset values", locator="rangesubset"):
        super(InvalidRangeSubSet, self).__init__(msg, locator)


class InvalidAxisLabel(WCSException):
    code = "InvalidAxisLabel"