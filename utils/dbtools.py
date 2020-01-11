# -*- coding: UTF-8 -*-


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [str(col[0], 'utf-8') for col in cursor.description]
    return [
        dict(list(zip(columns, row)))
        for row in cursor.fetchall()
    ]


def dictfetchone(cursor):
    "Return all rows from a cursor as a dict"
    columns = [str(col[0], 'utf-8') for col in cursor.description]
    row = cursor.fetchone()
    return dict(list(zip(columns, row))) if row else None
