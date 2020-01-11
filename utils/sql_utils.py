# -*- coding: utf-8 -*-



import os

from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
import django.forms as forms
from django.views.decorators.cache import cache_page

import datetime
# from django.http import HttpResponse, HttpResponseNotFound
# from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import connections, connection
# from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.db.models import F

from portal import models as pm
from portal import views as pv  # pv.error
from . import models
import utils.dbtools as dbt

import math
import re


class Reporter:
    ''' Утилиты для формирования отчетов по ТА в web'''

    # допустимые значения
    ACCEPTABLE_LEVEL = 99.5
    TARGET_LEVEL = 99.8
    MINIMUM = 99.4

    @staticmethod
    def get_datasets_by_lvls(serie, context={}):
        '''
        Разбивка значений на 3 уровня для раскраски
        :param serie:
        :param context:
        :return:
        '''
        ds = [[0 for y in range(len(serie))] for x in range(3)]
        sublegend = ['цель', 'допустимый', 'недопустимый']
        sublegend_option1 = ['не менее {}%'.format(Reporter.TARGET_LEVEL),
                             'менее {}%'.format(Reporter.TARGET_LEVEL),
                             'менее {}%'.format(Reporter.ACCEPTABLE_LEVEL),
                             ]

        counter = 0
        for val in serie:
            if val < Reporter.ACCEPTABLE_LEVEL:
                # недопустимые
                ds[2][counter] = val
            elif val < Reporter.TARGET_LEVEL:
                # допустимые
                ds[1][counter] = val
            else:
                # целевые
                ds[0][counter] = val
            counter += 1

        context.update(sublegend=sublegend, ds=ds, sublegend_option1=sublegend_option1)

    @staticmethod
    def execute_sql(sql, connection=connection, params=[], no_rows=False):
        cursor = connection.cursor()
        with cursor as c:
            if not params:
                c.execute(sql)
            else:
                c.execute(sql, params)
            if no_rows:
                return True
            return dbt.dictfetchall(c)

    @staticmethod
    def last_refresh_time(lock_model):
        last_refresh_time = None
        if lock_model.objects.all().count() > 0:
            last_refresh_time = lock_model.objects.all().order_by('-finished_at')[0]
        return last_refresh_time

    @staticmethod
    def check_lock(lock_model, request, text=None, *args, **kwargs):
        open_loads = lock_model.objects.filter(finished_at__isnull=True, **kwargs)
        if open_loads:
            if not text:
                text = 'Извините, идет обновление данных. Обновите страницу через 1-2 минуты.'
            return pv.error(request, text, *args, **kwargs)
        return None
