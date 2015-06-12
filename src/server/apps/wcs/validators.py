from dateutil import parser
import re

regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def is_valid_url(url):
    global regex
    return regex.search(url)


class DateValidator(object):
    def __init__(self, period, startyear, startday, dt="2000-01-01"):
        self.period = period
        self.startyear = startyear
        self.startday = startday
        self.dt = dt

    def __call__(self, date):
        return None


class DateToPoint(DateValidator):
    def __call__(self, date):
        """ Return an time index (timid) from the input date (MODIS DOY) and time period (e.g 8 days). """
        res = -1
        year = int(date[0:4])
        doy = int(date[4:7])
        ppy = int(365 / self.period) + 1  # Periods per year
        if self.period > 0 and (doy - 1) % self.period == 0:
            idd = (doy - 1) / self.period
            idy = (year - self.startyear) * ppy
            iii = (self.startday - 1) / self.period
            res = idy + idd - iii
        return res

    @staticmethod
    def format_to_day_of_year(date):
        dt = parser.parse(date)
        return "%s%s" % (dt.year,
                         dt.timetuple().tm_yday if dt.timetuple().tm_yday > 99 else '0' + str(dt.timetuple().tm_yday))
