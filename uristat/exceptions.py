# -*- coding: utf-8 -*-


from django.conf import settings

import portal.models as pm

URI_STAT_EXCEPTIONS = [
            settings.STATIC_URL,
            settings.MEDIA_URL,
            settings.CKEDITOR_UPLOAD_PATH,
            r'^/login/$',
            r'^/logout/$',
            r'^/password_change/$',
            r'^/password_change/done/$',
            r'^/ckeditor/',
            r'^/reporting/netcap/',
            r'^/admin/',
            r'^/comment/',
            r'^/' + pm.Section.cleaned_prefix() + r'/(all_docs|regulations|decrees|commands|memos'
                                             r'|records|instructions)/[1-9][0-9]*/*',
            r'^/' + pm.Section.cleaned_prefix() + r'/edo_report/'
            ]  # регулярки к путям