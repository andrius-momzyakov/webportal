# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.db import transaction
from django.conf import settings
from django.db.models import F

from reporting.views import Reporter
# Create your models here.

try:
    URI_LOGENTRY_RETAIN_DAYS = settings.URI_LOGENTRY_RETAIN_DAYS
except NameError:
    URI_LOGENTRY_RETAIN_DAYS = 3


class FollowLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    uri = models.CharField(verbose_name='URI', max_length=2048)
    ip = models.CharField(verbose_name='ip из запроса', max_length=15, null=True, blank=True)
    session_id = models.CharField(verbose_name='Id сессии', max_length=20, null=True, blank=True)
    # is_countable = models.BooleanField(verbose_name='Уникальное (считается в статистике)', default=False)
    log_time = models.DateTimeField(verbose_name='Время фиксации', default=datetime.datetime.now)
    stat_time = models.DateTimeField(verbose_name='Время обработки', null=True, blank=True)

    def __unicode__(self):
        return '{} - {} - {:%Y.%m.%d %H_%M_%S}'.format(self.uri, self.session_id, self.log_time)

    class Meta:
        verbose_name = 'Переход по ссылке'
        verbose_name_plural = 'Переходы по ссылкам'


class Stat(models.Model):
    uri = models.CharField(verbose_name='URI', max_length=2048)
    # fl_id = models.BigIntegerField(verbose_name='Последний обработанный Id для данного uri из лога')
    stat_time = models.DateTimeField(verbose_name='Время последнего расчета', default=datetime.datetime.now)
    cnt = models.BigIntegerField(verbose_name='Кол-во посещений')

    def __unicode__(self):
        return '{} - {} - {}'.format(self.uri, self.cnt, self.stat_time)

    @staticmethod
    def consistent_update():
        '''
        Запускать по расписанию. скрипт count_uristat.py
        :return:
        '''
        # набираем сырье из журнала
        with transaction.atomic():
            sql_log = '''
                lock table uristat_followlog IN share row exclusive MODE
            '''
            res = Reporter.execute_sql(sql_log, no_rows=True)

            sql_agr = '''
                lock table uristat_stat IN share row exclusive MODE
            '''
            res = Reporter.execute_sql(sql_log, no_rows=True)

            del_sql = '''
                delete from uristat_followlog 
                where log_time < (current_timestamp - interval '%s' day)
                and stat_time is NULL
            '''
            res = Reporter.execute_sql(del_sql, params=[URI_LOGENTRY_RETAIN_DAYS], no_rows=True)

            count_sql = '''
                select uri, count(*) cnt
                from
                (select uri, session_id, log_time- min(log_time) over (partition by uri, session_id) time_delta 
                from uristat_followlog where 
                stat_time is null
                ) q
                where time_delta = interval '0 seconds'
                group by 1
            '''
            rows = Reporter.execute_sql(count_sql)

            for row in rows:
                dt = datetime.datetime.now()
                try:
                    stat = Stat.objects.get(uri=row['uri'])
                    stat.stat_time = dt
                    stat.cnt = F('cnt') + row['cnt']
                except Stat.DoesNotExist:
                    stat = Stat(uri=row['uri'], cnt=0, stat_time=dt)
                    stat.cnt += row['cnt']
                stat.save()

                for entry in FollowLog.objects.filter(stat_time__isnull=True, uri=row['uri']):
                    entry.stat_time = dt
                    entry.save()

    class Meta:
        verbose_name = 'Счетчик посещений'
        verbose_name_plural = 'Счетчики посещений'
        unique_together = ['uri']



