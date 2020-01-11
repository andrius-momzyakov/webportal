# -*- coding: utf-8 -*-

import datetime
import re

from django.conf import settings

from . import models

import uristat.exceptions

try:
    URI_STAT_EXCEPTIONS = uristat.exceptions.URI_STAT_EXCEPTIONS
except:
    URI_STAT_EXCEPTIONS = []


class UriStatMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        stat_session_id = request.get_signed_cookie('stat_session_id', None)

        if not re.search('|'.join(URI_STAT_EXCEPTIONS), request.path_info):

            ip = ''
            if request.META.get('HTTP_X_FORWARDED_FOR', '') and request.META.get('REMOTE_ADDR', '') == '127.0.0.1':
                ip = request.META.get('HTTP_X_FORWARDED_FOR', '')
            else:
                ip = request.META.get('REMOTE_ADDR', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')

            log_entry = models.FollowLog(uri=request.path_info, ip=ip)
            log_entry.save()
            if not stat_session_id:
                stat_session_id = str(log_entry.pk)
                response.set_signed_cookie('stat_session_id', stat_session_id, max_age=30*60)
                # log_entry.is_countable = True

            log_entry.session_id = stat_session_id
            log_entry.save()

        return response
