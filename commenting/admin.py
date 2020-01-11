# -*- coding: utf-8 -*-


from django.contrib import admin

from commenting import models

# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_display = ['parent_url', 'commenter_email', 'commenter_name', 'created_at', 'updated_at', 'is_active']
    search_fields = ['parent_url', 'commenter_email', 'commenter_name']

admin.site.register(models.Comment, CommentAdmin)