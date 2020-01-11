# -*- coding: UTF-8 -*-
import portal as prtl

def portal(view):
    def wrapper(*args, **kwargs):
        # print kwargs
        context = kwargs.get('context')
        sec_id = kwargs.get('sec_id', None)  # уникальная метка раздела меню верхнего уровня для выделения
        if not context:
            context = {}
        if sec_id is not None and type(sec_id) is str:
            context.update(sec_id=sec_id)
        mm_items = prtl.models.MenuItem0.objects.all()  # TODO: В декоратор
        context.update(mm_items=mm_items)
        kwargs['context'] = context
        return view(*args, **kwargs)
    return wrapper


def add_news_nav(view):
    def wrapper(*args, **kwargs):
        context = kwargs.get('context')
        if not context:
            context = {}
        all_published = prtl.models.NewsEntry.objects.filter(publish=True, archive=False)
        context.update(published=all_published)
        kwargs['context'] = context
        return view(*args, **kwargs)
    return wrapper


def has_all_roles(roles):
    # global g_roles
    # g_roles = roles

    def wrapper1(func, g_roles=roles):

        def wrapper(*args, **kwargs):
            rq = args[0]
            grps = set([i['name'] for i in rq.user.groups.values('name')])
            roles = set(g_roles)
            if rq.user.is_superuser or roles.issubset(grps):
                return func(*args, **kwargs)
            # print [i['name'] for i in rq.user.groups.values('name')]
            from portal.views import error
            return error(rq, 'У Вас недосточно полномочий. Необходимо обратиться к администратору.',
                         back_uri=rq.META.get('HTTP_REFERER'), **kwargs)
        return wrapper

    return wrapper1


def portalctx(ctx_setter):
    '''
    Декоратор для формирования контекста для переопределенных стандартных auth views
    :param ctx_setter:
    :return:
    '''
    def wrapper(*args, **kwargs):
        context = kwargs.get('context')
        sec_id = kwargs.get('sec_id', None)  # уникальная метка раздела меню верхнего уровня для выделения
        # print 'sec_id', sec_id
        if not context:
            context = {}
        if sec_id is not None and type(sec_id) is str:
            context.update(sec_id=sec_id)
        else:
            context.update(sec_id='password_change')
        mm_items = prtl.models.MenuItem0.objects.all()  # TODO: В декоратор
        context.update(mm_items=mm_items)
        # print context
        return ctx_setter(*args, context=context, **kwargs)
    return wrapper


# def breadcrumb(view, title='', url=''):
#     def wrapper(*args, **kwargs):
#         if title:
#
#         uri_key = kwargs.get('uri_key', '')
#         if uri_key:
#             section = prtl.models.Section.get(uri_key)
#
#     return wrapper