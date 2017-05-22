from datetime import tzinfo, timedelta, datetime

ZERO = timedelta(0)
HOUR = timedelta(hours=1)

# A UTC class.

class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def __repr__(self):
        return "UTC"

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

utc = UTC()

# A class building tzinfo objects for fixed-offset time zones.
# Note that FixedOffset(0, "UTC") is a different way to build a
# UTC tzinfo object.

class FixedOffset(tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name):
        self.__offset = timedelta(minutes = offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO

# A class capturing the platform's idea of local time.

import time as _time

STDOFFSET = timedelta(seconds = -_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0

#Local = LocalTimezone()


# A complete implementation of current DST rules for major US time zones.

def first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt

def second_sunday_on_or_after(dt):
    days_to_go = 13 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt



class USTimeZone(tzinfo):

    def __init__(self, hours, reprname, stdname, dstname, DSTSTART, DSTEND):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname
        self.DSTSTART = DSTSTART
        self.DSTEND = DSTEND

    def __repr__(self):
        return self.reprname

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)

    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find second Sunday in March & the first in November.
        start = second_sunday_on_or_after(self.DSTSTART)
        end = first_sunday_on_or_after(self.DSTEND)

        # Can't compare naive to aware objects, so strip the timezone from
        # dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO


def construct_timezones(year):
    """Construct the time zones and return  them!"""
    
    YEAR = year
    # In the US, DST starts at 2am (standard time) on the second Sunday in March.
    DSTSTART = datetime(YEAR, 3, 7, 2)
    # and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
    DSTEND = datetime(YEAR, 11, 1, 1)
    
    Eastern  = USTimeZone(-5, "Eastern",  "EST", "EDT", DSTSTART, DSTEND)
    Central  = USTimeZone(-6, "Central",  "CST", "CDT", DSTSTART, DSTEND)
    Mountain = USTimeZone(-7, "Mountain", "MST", "MDT", DSTSTART, DSTEND)
    Pacific  = USTimeZone(-8, "Pacific",  "PST", "PDT", DSTSTART, DSTEND)
    
    return Pacific, Mountain, Central, Eastern,  utc
