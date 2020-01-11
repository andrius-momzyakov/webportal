# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponseRedirect

# Register your models here.

from . import models

admin.site.register(models.Section)
admin.site.register(models.MenuItem0)
admin.site.register(models.MenuItem1)
# admin.site.register(models.MenuItem2)


def news_to_top(modeladmin, request, queryset):
    for obj in queryset:
        obj.is_top = True
        obj.save()
news_to_top.short_description = 'В Топ!'


def news_from_top(modeladmin, request, queryset):
    for obj in queryset:
        obj.is_top = False
        obj.save()
news_from_top.short_description = 'Из Топа'


def news_to_archive(modeladmin, request, queryset):
    for obj in queryset:
        obj.archive = True
        obj.save()
news_to_archive.short_description = 'В архив'


def news_from_archive(modeladmin, request, queryset):
    for obj in queryset:
        obj.archive = False
        obj.save()
news_from_archive.short_description = 'Из архива'


class NewsAdmin(admin.ModelAdmin):
    model = models.NewsEntry
    list_display = ('title', 'day', 'region', 'publish', 'archive', 'is_top')
    exclude = ['created_by', 'updated_by', 'created_at', 'updated_at']
    actions = [news_to_top, news_from_top, news_to_archive, news_from_archive]


    def response_add(self, request, obj, post_url_continue="../%s/"):
        if '_continue' not in request.POST:
            # После добавления - в основной раздел документов на 1ю стр
            next_url = models.Section.PREFIX + r'news_summary/'
            return HttpResponseRedirect(next_url)
        else:
            return super(DocAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if '_continue' not in request.POST:
            # После ред-я - в основной раздел документов на 1ю стр
            next_url = models.Section.PREFIX + r'news_summary/'
            return HttpResponseRedirect(next_url)
        else:
            return super(DocAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)


admin.site.register(models.NewsEntry, NewsAdmin)
admin.site.register(models.PlainPage)
