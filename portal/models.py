# -*- coding: UTF-8 -*-


import os
import datetime as dt
from datetime import datetime
from datetime import date as dt_date
from django.contrib.auth.models import User
from django.db import models
#from urllib.parse import urljoin
from urllib.parse import urljoin

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

from django.db.models import Q

# Create your models here.

class ModelWithAuditFields(models.Model):
    created_by = models.ForeignKey(User, related_name='creator', verbose_name='Кем создано', blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='updater', verbose_name='Кем изменено', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Когда создано', null=True, blank=True, default=datetime.now)
    updated_at = models.DateTimeField(verbose_name='Когда изменено', null=True, blank=True)

    def save(self, user=None, *args, **kwargs):
        _user = None
        _dt = datetime.now()
        if not isinstance(user, User):
            if type(user) is int:
                try:
                    _user = User.objects.get(pk=user)
                except User.DoesNotExist:
                    pass
        else:
            _user = user
        if self.pk == None:  #новая запись
            self.created_by = _user
        else:
            self.updated_by = _user
            self.updated_at = _dt
        super(ModelWithAuditFields, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class Section(models.Model):
    """
    Элементы меню верхнего уровня для портала
    model_ref пример: {"model": "OrgUnit", "key":"pk", "value":"2"}
    uri_key = ключ для портальных разделов с фикс. префиксом и параметром uri_key.
        для  разделов с full_uri uri_key = full_uri !!!
    full_uri = полный путь для uri, не использующих фикс. префикс
    """

    PREFIX = '/portal/'

    uri_key = models.CharField(verbose_name='Ключевое значение URI', max_length=36, blank=True, unique=True)
    full_uri = models.CharField(verbose_name='Полный путь', max_length=36, null=True, blank=True)
    get_params = models.CharField(verbose_name='Дополнительные get-параметры (в строку)', max_length=2000, null=True,
                                  blank=True)
    title = models.TextField(verbose_name='Наименование раздела (текст для исп. в меню и ссылках)')
    page = models.ForeignKey('PlainPage', verbose_name='Страница (HTML)', null=True, blank=True)
    model_ref = models.CharField(verbose_name='Ссылка на модель (JSON)', max_length=2000, null=True, blank=True)
    parent = models.ForeignKey('self', verbose_name='Раздел верхнего уровня', null=True, blank=True)  # Для
    # динамического формирования хлебных крошек

    def save(self, *args, **kwargs):
        super(Section, self).save(*args, **kwargs)
        if not self.uri_key:
            self.uri_key = self.full_uri if self.full_uri else str(self.pk)
            super(Section, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def uri(self):
        res = ''
        if not self.full_uri or len(self.full_uri) == 0:
            res = urljoin(self.__class__.PREFIX, self.uri_key)
        else:
            res = self.full_uri
        if self.get_params and len(self.get_params) > 0:
            pars = self.get_params
            if pars[0] != '?':
                pars = '?' + pars
            res += pars
        return res

    @staticmethod
    def cleaned_prefix():
        return Section.PREFIX.replace('/', '')

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'


class MenuItem0(models.Model):
    '''
    Элементы меню первого уровня
    '''

    SUBMENU_APPEARANCE = (('submenu', 'Субменю'), ('dropdown', 'Выпадающее'))

    label = models.CharField(verbose_name='Метка', max_length=80, null=True, blank=True)
    html_label = models.TextField(verbose_name='Метка (html)', max_length=200, null=True, blank=True)
    section = models.ForeignKey(Section, verbose_name='Раздел', null=True, blank=True)
    appearance = models.CharField(verbose_name='Представление для меню 2го ур.', max_length=50,
                                  choices=SUBMENU_APPEARANCE, default='dropdown')
    order = models.IntegerField(verbose_name='Ключ для сортировки', null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Активно', blank=True, default=True)
    is_prototype = models.BooleanField(verbose_name='Показывать как прототип', blank=True, default=True)
    groups = models.CharField(verbose_name='Группы (через ",")', max_length=1000, blank=True, null=True)
    authenticated_access = models.BooleanField(verbose_name='Для залогиненных only', blank=True, default=False)

    def __unicode__(self):
        return self.label + (lambda: ' - ОТКЛ' if not self.is_active else '')()

    def uri(self):
        if self.section:
            return self.section.uri()

    def children_all(self):
        return MenuItem1.objects.filter(menu=self)

    def children(self):
        return MenuItem1.objects.filter(Q(is_active=True) | Q(is_prototype=True), menu=self)

    @staticmethod
    def get_items_by_groups(qs, checked_groups):
        if type(checked_groups) is str:
            checked_groups = checked_groups.split(',')
        else:
            checked_groups = checked_groups
        res = []
        qs = qs
        for mi in qs:
            if mi.groups is None or len(mi.groups) == 0:
                res.append(mi)
            else:
                grps = mi.groups.split(',')
                if len(set(grps).intersection(checked_groups)) > 0:
                    res.append(mi)
        return res


    class Meta:
        verbose_name = 'Элемент меню 1го уровня'
        verbose_name_plural = 'Элементы меню 1го уровня'
        ordering = ['order', 'pk']


class MenuItem1(models.Model):
    '''
    Элементы меню второго уровня
    '''

    label = models.CharField(verbose_name='Метка', max_length=120)
    section = models.ForeignKey(Section, verbose_name='Раздел', null=True, blank=True)
    menu = models.ForeignKey(MenuItem0, verbose_name='Меню верхнего уровня', null=True)
    divider = models.BooleanField(verbose_name="Поставить разделитель после", default=False)
    order = models.IntegerField(verbose_name='Ключ для сортировки', null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Активно', blank=True, default=True)
    is_prototype = models.BooleanField(verbose_name='Показывать как прототип', blank=True, default=False)
    groups = models.CharField(verbose_name='Группы (через ",")', max_length=1000, blank=True, null=True)
    authenticated_access = models.BooleanField(verbose_name='Для залогиненных only', blank=True, default=False)

    def __unicode__(self):
        if self.is_active:
            return '{} @ {}'.format(self.label, self.menu.label)
        else:
            return '{} @ {} - ОТКЛ'.format(self.label, self.menu.label)

    class Meta:
        ordering = ['order', 'pk']
        verbose_name = 'Элемент меню 2го уровня'
        verbose_name_plural = 'Элементы меню 2го уровня'

"""
class MenuItem2(models.Model):
    '''
    Элементы меню третьего уровня - НЕ используются
    '''

    label = models.CharField(verbose_name=u'Метка', max_length=120)
    section = models.ForeignKey(Section, verbose_name=u'Раздел', null=True, blank=True)
    menu = models.ForeignKey(MenuItem1, verbose_name=u'Меню верхнего уровня', null=True)
    divider = models.BooleanField(verbose_name=u"Поставить разделитель после", default=False)
    order = models.IntegerField(verbose_name=u'Ключ для сортировки', null=True, blank=True)
    is_active = models.BooleanField(verbose_name=u'Активно', blank=True, default=True)

    def __str__(self):
        if self.is_active:
            return '{} @ {} @ {}'.format(self.label, self.menu.label, self.menu.menu.label)
        return '{} @ {} @ {} - ОТКЛ'.format(self.label, self.menu.label, self.menu.menu.label)

    class Meta:
        ordering = ['order', 'pk']
        verbose_name = u'Элемент меню 3го уровня'
        verbose_name_plural = u'Элементы меню 3го уровня'
"""


class NewsEntry(ModelWithAuditFields):
    # parent = models.OneToOneField(ModelWithAuditFields, parent_link=True, related_name='news_entry')
    region = models.ForeignKey(Region, verbose_name='Регион', null=True, blank=True)
    day = models.DateTimeField(verbose_name='Дата публикации новости',
                               default=datetime.now)
    title = models.CharField(verbose_name='Заголовок', max_length=500)
    preview_txt = RichTextUploadingField(verbose_name='Анонс', null=True, blank=True, config_name='basic')
    preview_img = models.ImageField(verbose_name='Картинка к анонсу', upload_to='news_preview/%Y/%m/%d/', null=True,
                                    blank=True)
    preview_img_width_pct = models.IntegerField(verbose_name='Ширина превьюшки в % от ширины контейнера', default=50)
    publish = models.BooleanField(verbose_name='Опубликовать', blank=True, default=False)
    archive = models.BooleanField(verbose_name='В архиве', blank=True, default=False)
    is_top = models.BooleanField(verbose_name='Новость дня', blank=True, default=False)
    is_regulation_change = models.BooleanField(verbose_name='Изменение в нормативных документах', blank=True,
                                               default=False)
    comments_allowed = models.BooleanField(verbose_name='Разрешить каменты', default=True)
    body = RichTextUploadingField(verbose_name='Текст', blank=True, null=True)

    created_by = models.ForeignKey(User, related_name='site_report_creator', verbose_name='Кем создано', blank=True,
                                   null=True)
    updated_by = models.ForeignKey(User, related_name='site_report_updater', verbose_name='Кем изменено', blank=True,
                                   null=True)


    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-day', '-id']

    def __unicode__(self):
        return '{} {:%d.%m.%Y %H_%M_%S} {}'.format(self.title, self.day, (lambda: self.created_by if self.created_by else '')())

    def get_absolute_url(self):
        return r'/' + Section.cleaned_prefix() + r'/news/{}/'.format(self.pk)

    def comments_cnt(self):
        from commenting.models import Comment
        return Comment.objects.filter(parent_url=self.get_absolute_url()).count()

    def comments(self):
        from commenting.models import Comment
        return Comment.objects.filter(parent_url=self.get_absolute_url())

    @staticmethod
    def last_n_cc_news(n=20):
        return NewsEntry.objects.filter(publish=True, archive=False, region__isnull=True)[:n]

    @staticmethod
    def cc_top_news():
        return NewsEntry.objects.filter(publish=True, archive=False, region__isnull=True, is_top=True)

    @staticmethod
    def regional_top_news():
        return NewsEntry.objects.filter(publish=True, archive=False, region__isnull=False, is_top=True)

    @staticmethod
    def last_n_regional_news(n=10):
        return NewsEntry.objects.filter(publish=True, archive=False, region__isnull=False)[:n]

    @staticmethod
    def last_n_regulational_news(n=10):
        return NewsEntry.objects.filter(publish=True, archive=False, is_regulation_change=True)[:n]
