# -*- coding: utf-8 -*-



import re

SHITTIES = ['ООО', 'ПАО', 'АО']

def clean_orgname(val):
    # print '|'.join(['\s+' + shit + '\s*' for shit in SHITTIES])
    res = re.sub('|'.join(['\s+' + shit + '\s*' for shit in SHITTIES]), '', val)
    res = ' '.join(res.split())
    return res
