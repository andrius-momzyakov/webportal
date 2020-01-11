# -*- coding: utf-8 -*-


# Import smtplib for the actual sending function
import smtplib, email

# Import the email modules we'll need
from email.mime.text import MIMEText

from redis import Redis
from rq import Queue
from rq.decorators import job
from django.conf import settings


def notify(subject=None, text=None, sender=None, to=[]):
    # print text
    msg = MIMEText(text, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    try:
        s.sendmail(sender, to, msg.as_string())
    except smtplib.SMTPDataError as e:
        print(msg.as_string())
        print('SMTP:', e)
    except Exception as e:
        print(type(e), e.message)
    finally:
        s.quit()

def notify_test(subject=None, text=None, sender=None, to=[]):

    msg = MIMEText('test')
    msg['Subject'] = 'test'
    msg['From'] = 'mirta@mts.ru'
    msg['To'] = 'aymomzya@mts.ru'

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(sender, to, msg.as_string())
    s.quit()


def enqueue_notification(subject=None, text=None, sender=None, to=[], queue='medium'):
    try:
        if settings.ASYNC_NOTIFICATIONS:
            is_async = True
        else:
            is_async = False
    except AttributeError:
        is_async = False
    q = Queue(queue, is_async=is_async, connection=Redis())
    result = q.enqueue(notify, subject=subject, text=text, sender=sender, to=to)

