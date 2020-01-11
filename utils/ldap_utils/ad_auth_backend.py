# -*- coding: utf-8 -*-



from . import authenticate, LDAP_INVALID_CREDENTIALS
from ldap import SERVER_DOWN
from django.contrib.auth.models import User, Permission, Group
from django.db import connection
from reporting.views import Reporter


class AdAuthBackend(object):

    def authenticate(self, request, username=None, password=None):

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        try:
            if authenticate(username, password):
                return user
        except LDAP_INVALID_CREDENTIALS:
            return None
        except SERVER_DOWN as e:
            # print str(e)
            raise e

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active:
            return []
        a = [p.codename for p in Permission.objects.filter(user=user_obj)]
        groups = [g.name for g in user_obj.groups.all()]
        b = [p.codename() for p in [g.permissions.all() for g in groups]]
        return a + b

    def get_group_permissions(self, user_obj, obj=None):
        if not user_obj.is_active:
            return []
        groups = [g.name for g in user_obj.groups.all()]
        return [p.codename() for p in [g.permissions.all() for g in groups]]

    def has_module_perms(self, user_obj, package_name):
        if not user_obj.is_active:
            return False
        model_codes = ['_'.join(p.codename.split('_')[1:]) for p in Permission.objects.filter(user=user_obj)]
        placeholders = ','.join(['%s' for _ in range(len(model_codes))])
        sql = '''
            select distinct app_label 
            from django_content_type 
            where model in ({})
        '''.format(placeholders)
        conn = connection
        rows = Reporter.execute_sql(sql, connection=conn, params=model_codes)
        app_codes = [v for v in [list(row.values()) for row in rows]]
        return package_name in app_codes

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        return perm.split('.')[1] in [p.codename for p in Permission.objects.filter(user=user_obj)]
