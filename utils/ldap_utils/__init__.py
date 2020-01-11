# -*- coding: utf-8 -*-


import re

import ldap
from django.conf import settings

'''
settings.py
===========

LDAP_URI = 'ldap://ldap.kontora.ru'
LDAP_VER_NO = 3  # номер версии LDAP - 2 или 3
LDAP_USER_DOMAIN = 'kontora.ru'
'''


class LDAP_MISCONFIGURED(Exception):

    def __init__(self, msg=None):
        if not msg:
            self.error = 'Подключение к LDAP невозможно, т.к. не заданы/неверно заданы параметры settings.LDAP_URI ' \
                     'и settings.LDAP_VER_NO.'
        else:
            self.error = msg

    def __str__(self):
        return self.error.encode('utf-8')


class LDAP_INVALID_CREDENTIALS(Exception):

    def __init__(self, msg=None):
        if not msg:
            self.error = 'Указаны неверные имя пользователя или пароль.'
        else:
            self.error = msg

    def __str__(self):
        return self.error.encode('utf-8')


try:
    LDAP_AUTH_PARAMS = settings.LDAP_AUTH_PARAMS
except AttributeError:
    raise LDAP_MISCONFIGURED(msg='В settings не задан словарь LDAP_AUTH_PARAMS.')

ldap_uri = LDAP_AUTH_PARAMS.get('uri')
if not ldap_uri:
    raise LDAP_MISCONFIGURED(msg='Не задан uri ldap-сервера.')
ver_no = LDAP_AUTH_PARAMS.get('ldap_version', 3)
ldap_version = ldap.VERSION3 if ver_no == 3 else ldap.VERSION2 if ver_no == 2 else ldap.VERSION1
ldap_user_domain = LDAP_AUTH_PARAMS.get('ldap_users_domain', '')
if not ldap_user_domain:
    raise LDAP_MISCONFIGURED(msg='Не задан ldap_users_domain.')
tech_account_dn = LDAP_AUTH_PARAMS.get('tech_account_dn', '')
if not tech_account_dn:
    raise LDAP_MISCONFIGURED(msg='Не задан tech_account_dn.')
tech_account_password = LDAP_AUTH_PARAMS.get('tech_account_password', '')
ldap_user_search_attr = LDAP_AUTH_PARAMS.get('ldap_user_search_attr', '')
if not ldap_user_search_attr:
    raise LDAP_MISCONFIGURED(msg='Не задан ldap_user_search_attr.')


def authenticate(username, password):
    ldap_connection = ldap.initialize(ldap_uri)
    ldap_connection.set_option(ldap.OPT_REFERRALS, 0)
    ldap_connection.protocol_version = ldap_version
    base_dn = ldap_user_domain
    try:
        bind_res = ldap_connection.simple_bind_s(tech_account_dn, tech_account_password)
    except ldap.INVALID_CREDENTIALS:
        raise LDAP_INVALID_CREDENTIALS(msg='Неверные учетные данные tech_account_dn.')
    try:
        srch_res = ldap_connection.search_s(base_dn, ldap.SCOPE_SUBTREE, '({}={})'.format(ldap_user_search_attr,
                                                                                      username))
        if len(srch_res) != 1:
            ldap_connection.unbind_s()
            raise LDAP_INVALID_CREDENTIALS(msg='Неверные учетные данные {}'.format(username))
        user_dn = srch_res[0][0]
        res = ldap_connection.simple_bind_s(user_dn, password)
        ldap_connection.unbind_s()
        return True
    except ldap.INVALID_CREDENTIALS:
        ldap_connection.unbind_s()
        raise LDAP_INVALID_CREDENTIALS
