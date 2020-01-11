def number_format(val):
    if val:
        return '{0:,}'.format(val).replace(',', '&nbsp;').replace('.', ',')
    return ''
