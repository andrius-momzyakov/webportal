# -*- coding: UTF-8 -*-

import sys, traceback
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
import django.forms as forms
from django.contrib.auth.decorators import login_required

from datetime import datetime as dt
import datetime
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import ValidationError

from . import models
from .models import SiteReport, NewsEntry, SiteReportViewLock,\
                    Document, InfoSystem, SiteReportLoad, ManualNav, Section, PlainPage,\
                    OrgUnit
from utils.portal_decorators import portal, add_news_nav, has_all_roles
from utils.pagenav import PageNav
from django.db.models import Q

import math
import json
import re

# import news_views1
# Create your views here.


def render_plainpage(request, uri_key='', template='plainpage.html', context={}):
    section = get_object_or_404(Section, uri_key=uri_key)
    context.update(section=section)
    return render(request, template, context=context)


@portal
def handler404(request, exception, *args, **kwargs):
    # return HttpResponseNotFound
    response = render(request, template_name='404.html', context=kwargs.get('context'))
    response.status_code = 404
    return response


@portal
def handler500(request, *args, **kwargs):
    # return HttpResponseServerError
    message = 'Извините, что-то пошло не так ...'
    context = kwargs.get('context', {})
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)
    # print data
    if not exc_type:
        context.update(message=message)
    else:
        message = 'В приложении произошла ошибка с кодом 500:'
        context.update(message=message, tb=tb)
    response = render(request, template_name='500.html', context=context)
    response.status_code = 500
    return response


@portal
def error(request, text, back_uri='',  *args, **kwargs):
    context = kwargs.get('context', {})
    context.update(text=text, back_uri=back_uri)
    return render(request, template_name='error.html', context=context)


@portal
@add_news_nav
def home(request, context={}, *args, **kwargs):
    uri_key = 'home'
    return redirect('{}{}/'.format(Section.PREFIX, uri_key))


@portal
@add_news_nav
def portal_page(request, uri_key='', context={}, prefix='', xls_flag=None, drilldown=None, *args, **kwargs):

    qry_original = request.GET.urlencode()
    qry = qry_original
    if len(qry_original) > 0:
        qry = '?' + qry_original

    if uri_key == 'home':
        return render_plainpage(request, uri_key=uri_key, template='home.html', context=context)

    if uri_key == 'news_summary':
        from .news_views import news_summary
        return news_summary(request, uri_key=uri_key, context=context, prefix=prefix, *args, **kwargs)

    if uri_key == 'news_archive':
        from .news_views import news_archive
        return news_archive(request, uri_key=uri_key, context=context, prefix=prefix, *args, **kwargs)

    raise Http404('К большому сожалению, раздел {} не найден.'.format(uri_key))


@portal
@add_news_nav
def news_view(request, id, context={}, *args, **kwargs):
    back_uri = request.META.get('HTTP_REFERER')
    news = get_object_or_404(NewsEntry, pk=id)
    if not request.user.is_authenticated \
        and  not news.publish:
        return error(request, text='Данная новость недоступна анонимным посетителям, так как не опубликована.',
                     back_uri=back_uri)
        # all_published = NewsEntry.objects.filter(publish=True, archive=False)
    # context.update(published=all_published, news=news, back_uri=back_uri)
    context.update(news=news, back_uri=back_uri)
    from commenting.models import Comment
    parent_url = request.path_info
    parent_url += '?{}'.format(request.GET.urlencode()) if request.GET else ''
    # print 'parent_url', parent_url
    comments = Comment.objects.filter(parent_url=parent_url, is_active=True)
    comments_list = []
    for c in comments:
        if c.confirmation_token in request.get_signed_cookie('fresh_comments', '').split(','):
                                                              # .session.get('fresh_comments', '').split(','):
            c.edit_flag = True
            from commenting.views import EditCommentForm
            c.edit_form = EditCommentForm(instance=c)
        else:
            c.edit_flag = False
        comments_list.append(c)
    from commenting.views import AddCommentForm
    context.update(comments=comments_list, add_comment_form=AddCommentForm(initial={'parent_url': parent_url}))
    return render(request, 'news.html', context=context)


