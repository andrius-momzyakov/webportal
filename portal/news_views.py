# -*- coding: UTF-8 -*-

from django.shortcuts import render #, get_object_or_404
from django.http import Http404
import django.forms as forms

# from datetime import datetime as dt
# import datetime
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import ValidationError


from .models import Section,  NewsEntry
# from utils.portal_decorators import portal, add_news_nav
from utils.pagenav import PageNav

import math

NEWS_TABS_REFS = ['news_summary/', 'regional_news/', 'news_archive/']
NEWS_TABS_REFS = [Section.PREFIX + x for x in NEWS_TABS_REFS]


def news_matrix(news_list, entries_in_row):
    news_matrix = []
    news_list_cnt = len(news_list)
    rows_cnt = int(math.ceil(news_list_cnt / entries_in_row))
    for row in range(rows_cnt):
        new_row = []
        for col in range(entries_in_row):
            if news_list_cnt > 0:
                try:
                    # value = news_list.pop()
                    e = news_list.pop(0)
                    new_row.append(e)
                    # print e
                except IndexError:
                    new_row.append(None)
        news_matrix[len(news_matrix):] = [new_row]
    return news_matrix


def news_trmatrix(news_matrix):
    news_trmatrix = []
    if len(news_matrix) > 0:
        cols = [col for col in range(len(news_matrix[0]))]
        rows = [row for row in range(len(news_matrix))]
        for col in cols:
            new_row = []
            for row in rows:
                new_row.append(news_matrix[row][col])
            news_trmatrix[len(news_trmatrix):] = [new_row]
    return news_trmatrix


def news_archive(request, uri_key='', context={}, prefix='', *args, **kwargs):

    ITEMS_ON_PAGE = 20
    ORDERABLE = ['title', 'day', 'preview_txt']

    def validate_page_size(value):
        if value <= 0:
            raise ValidationError('Размер страницы д.б. натуральным числом.')


    class DateSelectorForm(forms.Form):

        def __init__(self, *args, **kwargs):
            super(DateSelectorForm, self).__init__(*args, **kwargs)
            years = [(d.year, str(d.year)) for d in NewsEntry.objects.filter(archive=True, publish=True). \
                order_by('-day').dates('day', 'year')] + [(None, '--------')]
            self.fields['year'] = forms.ChoiceField(label='Год', required=False, choices=years)
            months = [('{}/{}'.format(d.year, d.month), '{}/{}'.format(d.year, d.month)) for d in NewsEntry.objects. \
                filter(archive=True, publish=True). \
                order_by('-day').dates('day', 'month')] + [(None, '--------')]
            self.fields['month'] = forms.ChoiceField(label='Месяц', required=False, choices=months)
            days = [(d, '{}/{}/{}'.format(d.year, d.month, d.day)) for d in NewsEntry.objects. \
                filter(archive=True, publish=True). \
                order_by('-day').dates('day', 'day')] + [(None, '--------')]
            self.fields['date_from'] = forms.ChoiceField(label='Дата пуб. с', required=False, choices=days)
            self.fields['date_to'] = forms.ChoiceField(label='до', required=False, choices=days)
            sizes = ((10, '10'), (20, '20'), (None, '30'), (50, '50'), (100, '100') )
            self.fields['page_size'] = forms.ChoiceField(label='Док.на стр.',
                                                         initial=None, #ITEMS_ON_PAGE,
                                                         choices=sizes, required=False
                                                         # validators=[validate_page_size]
                                                         )

            for visible in self.visible_fields():
                visible.field.widget.attrs['class'] = 'form-control form-control-sm ml-1'


    qry = request.GET.urlencode()
    if len(qry) > 0:
        qry = '?' + qry

    news_list = NewsEntry.objects.filter(publish=True, archive=True)

    # ********************************************************
    from utils.tbltools import apply_ordering_tools
    res = apply_ordering_tools(request, qs=news_list, headers=ORDERABLE,
                               order_session_var='archive_news_order')
    if res.get('redirect_url'):
        return (redirect(res.get('redirect_url')))

    news_list = res.get('qs')
    order_params = res.get('order_params')
    context.update(order_params=order_params)
    # ********************************************************

    if request.GET:
        form = DateSelectorForm(request.GET)
        if form.is_valid():
            year = form.cleaned_data['year']
            year = int(year) if year else None
            myear, month = form.cleaned_data['month'].split('/') if form.cleaned_data['month'] else (None, None)
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']

            ITEMS_ON_PAGE = form.cleaned_data['page_size'] if form.cleaned_data['page_size'] else ITEMS_ON_PAGE

            if year:
                news_list = news_list.filter(day__year=year)
            if myear and month:
                news_list = news_list.filter(day__year=int(myear), day__month=int(month))
            if date_from:
                news_list = news_list.filter(day__date__gte=date_from)
            if date_to:
                news_list = news_list.filter(day__date__lte=date_to)
        else:
            return HttpResponse('Oops!')

    else:
        form = DateSelectorForm()

    pagenum = int(kwargs.get('pagenum', 1))
    paginator = Paginator(news_list, ITEMS_ON_PAGE)
    # news_list_page = paginator.page(pagenum)
    pagnav = None
    try:
        paginator_page = paginator.page(pagenum)
    except EmptyPage:
        pagenum = 1
        paginator_page = paginator.page(pagenum)
    try:
        url_template = r'/' + Section.cleaned_prefix() + r'/{uri_key}/{pagenum}/' + qry
        url_template = url_template.format(uri_key=uri_key, pagenum='{page}')
        pagnav = PageNav(pagenum, paginator_page=paginator_page,
                         url_template=url_template)
    except ValueError:
        raise Http404

    context.update(my_page_nav=pagnav)

    context.update(news_list=pagnav.paginator_page)
    context.update(active_tab='news_archive')
    context.update(form=form)
    context.update(news_tabs_refs=NEWS_TABS_REFS)

    return render(request, 'archivenews_nav.html', context=context)


def news_summary(request, uri_key='', context={}, prefix='', *args, **kwargs):
    news_list = list(NewsEntry.cc_top_news())
    # news_list = NewsEntry.last_n_cc_news(n=20)
    # cc_top_news = NewsEntry.cc_top_news()
    NEWS_ENTRIES_IN_ROW = 3

    news_matrix_ = news_matrix(news_list, entries_in_row=NEWS_ENTRIES_IN_ROW)
    context.update(news_matrix=news_matrix_)

    news_trmatrix_ = news_trmatrix(news_matrix=news_matrix_)
    # print news_matrix
    # print news_trmatrix
    context.update(news_trmatrix=news_trmatrix_)
    context.update(active_tab='news_summary')
    context.update(news_tabs_refs=NEWS_TABS_REFS)

    return render(request, 'news_nav.html', context=context)


def regional_news(request, uri_key='', context={}, prefix='', *args, **kwargs):
    news_list = list(NewsEntry.regional_top_news())
    # cc_top_news = NewsEntry.cc_top_news()
    NEWS_ENTRIES_IN_ROW = 3

    news_matrix_ = news_matrix(news_list, entries_in_row=NEWS_ENTRIES_IN_ROW)
    context.update(news_matrix=news_matrix_)

    news_trmatrix_ = news_trmatrix(news_matrix=news_matrix_)
    context.update(news_trmatrix=news_trmatrix_)
    context.update(active_tab='regional_news')
    context.update(news_tabs_refs=NEWS_TABS_REFS)

    return render(request, 'news_nav.html', context=context)
