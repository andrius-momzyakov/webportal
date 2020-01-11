from django.conf import settings

import datetime
import pytz
import calendar


def to_current_tz(dt):
    if not dt:
        return None
    tz = pytz.timezone(settings.TIME_ZONE)
    return dt.astimezone(tz)


def month_and_year(d):
    return (d.month, d.year)


def month_boundaries(month, year):
    fwd, mdays = calendar.monthrange(year=year, month=month)
    start_date = datetime.date(year=year, month=month, day=1)
    end_date = datetime.date(year=year, month=month, day=mdays)
    return (start_date, end_date)


def decrement_one_month(month, year):
    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1
    return month, year


def increment_one_month(month, year):
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1
    return month, year


