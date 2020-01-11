# -*- coding: utf-8 -*-

import re

from django.conf import settings
from uristat.models import Stat
import uristat.exceptions

try:
    URI_STAT_SHOW = settings.URI_STAT_SHOW
except NameError:
    URI_STAT_SHOW = True
except AttributeError:
    URI_STAT_SHOW = False

try:
    URI_STAT_EXCEPTIONS = uristat.exceptions.URI_STAT_EXCEPTIONS
except NameError:
    URI_STAT_EXCEPTIONS = []
except AttributeError:
    URI_STAT_EXCEPTIONS = []


def uristat_cnt(request):
    # print '|'.join(['{}'.format(item) for item in URI_STAT_EXCEPTIONS])
    # print request.path_info
    if not URI_STAT_SHOW:
        return {}

    if not re.search('|'.join(URI_STAT_EXCEPTIONS), request.path_info):
        try:
            stat = Stat.objects.get(uri=request.path_info)
            last_digit = int(str(stat.cnt)[len(str(stat.cnt)) - 1])
            verb = ' раз' if last_digit in [0, 1] + list(range(5, 10)) else ' раза'
            return {'uristat_cnt': stat.cnt, 'uristat_times_verbose': verb, 'uristat_show': URI_STAT_SHOW}
        except Stat.DoesNotExist:
            return {'uristat_cnt': 0, 'uristat_times_verbose': ' раз', 'uristat_show': URI_STAT_SHOW}
    return {}
