# project-1
Django-based typical web-application's template project 
## Project wide config
1. Notifications module (utils) depends on Redis and rq.
```
ASYNC_NOTIFICATIONS = False # or True on *NIX
```
## uristat application
#### settings.py
```
MIDDLEWARE = [
    ...,
    'uristat.uristat_middleware.UriStatMiddleware'
]
```
```
TEMPLATES = [
    {
        ...,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'uristat.context_processors.uristat_cnt',
            ],
        },
    },
]
```
```
INSTALLED_APPS = [ 
    ...,
    'uristat',
    ...
]    
```
## reg application
#### settings.py
```
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```
#### urls.py
```
urlpatterns = [
    ...,
    url(r'^login/$', mLoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^password_change/$', mPasswordChangeView.as_view(), name='password_change'),
    url(r'^password_change/done/$', mPasswordChangeDoneView.as_view(), name='password_change_done'),
    ...
]
```
## Commenting app
#### settings.py
```
...
SERVER_NAME = 'http://127.0.0.1:8000'    # or other
URI_LOGENTRY_RETAIN_DAYS = 3  # Days to retain entry in log before deletion.
URI_STAT_SHOW = True  # sitewide setting
...
```
#### views.py
In a view:
```
    ...
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

```
## CKEditor
Must be installed and configured for other dependants like `commenting` app.
#### settings.py
```
INSTALLED_APPS = [
    ...
    'ckeditor', 
    'ckeditor_uploader',
    ...
]
```
```
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'allowedContent': True,
    },
    'basic': {
        'toolbar': [[
                    # "Format",
                    "Bold", "Italic", "Underline", "Strike", "SpellChecker"],
                [
                    #'NumberedList', 'BulletedList',
                    "Indent", "Outdent", 'JustifyLeft', 'JustifyCenter',
                 'JustifyRight', 'JustifyBlock'],
                # ["Image", "Table", "Link", "Unlink", "Anchor", "SectionLink", "Subscript", "Superscript"],
                    ['Undo', 'Redo'], ["Source"],
                ["Maximize"]],
    },
    'comment': {
        'toolbar': [
            ['Bold', 'Italic', 'Underline', "Strike", "SpellChecker"],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter',
             'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat'] #, 'Source']
        ],
        'allowedContent': True,
    },
}
...
CKEDITOR_UPLOAD_PATH = 'ck-gallery/'
CKEDITOR_UPLOAD_SLUGIFY_FILENAME = False
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_IMAGE_BACKEND = 'Pillow'
...
```
## Paginator usage by example 
### in a template
```
        <table>
        ...
        </table>
        {% include 'paginator.html' %}
```
### in a view
```
    ...
    
    qs = qs.order_by('fld1', ...)
    pagenum = int(kwargs.get('pagenum', 1))
    paginator = Paginator(qs, ITEMS_ON_PAGE,)
    try:
        paginator_page = paginator.page(pagenum) 
    except EmptyPage:
        pagenum = paginator.num_pages
        paginator_page = paginator.page(pagenum)
    try:
        url_template = r'/' + Section.cleaned_prefix() + r'/{uri_key}/{pagenum}/' + qry
        url_template = url_template.format(uri_key=uri_key, pagenum='{page}')  # для шаблона!
        pagnav = PageNav(pagenum, paginator_page=paginator_page,
                         url_template=url_template)
    except ValueError:
        raise Http404

    context.update( ...
        my_page_nav=pagnav, # paginator object
        contracts=pagnav.paginator_page, # page of paginated queryset
         ...
    )

    return render(request, 'report.html', context=context)
```
