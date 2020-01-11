# -*- coding: utf-8 -*-


import uuid

from django.db import models, IntegrityError

from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings

from portal import models as pm
from utils import notifications as ntf

try:
    ASYNC_NOTIFICATIONS = settings.ASYNC_NOTIFICATIONS
except AttributeError:
    ASYNC_NOTIFICATIONS = False

try:
    SERVER_NAME = settings.SERVER_NAME
except AttributeError:
    SERVER_NAME = 'http://127.0.0.1:8000'

# Create your models here.

class Comment(pm.ModelWithAuditFields):
    CONFIRM_URL_PREFIX = 'comment/confirm'

    commenter_email = models.EmailField(verbose_name='Ваш e-mail@mts.ru')
    commenter_name = models.CharField(verbose_name='Ваше имя', max_length=250)
    body = RichTextField(verbose_name='Текст комментария (<=2000 символов)', max_length=2000, config_name='basic')
    parent_url = models.CharField(verbose_name='Url для привязки (<=2048 символов)', max_length=2048)
    confirmation_token = models.CharField(verbose_name='Ключ подтверждения', max_length=100, unique=True)
    is_active = models.BooleanField(verbose_name='Запись активна', default=False)
    created_by = models.ForeignKey(User, related_name='cmmnt_creator', verbose_name='Кем создано', blank=True,
                                   null=True)
    updated_by = models.ForeignKey(User, related_name='cmmnt_updater', verbose_name='Кем изменено', blank=True,
                                   null=True)

    def __unicode__(self):
        return '{} {} {}'.format(self.commenter_email, self.commenter_name, self.body[:50])

    def confirm_url(self):
        return (SERVER_NAME + '/' + self.__class__.CONFIRM_URL_PREFIX + '/' +
                self.confirmation_token + '/').encode('utf-8', 'ignore')

    def full_parent_url(self):
        return (SERVER_NAME + self.parent_url).encode('utf-8', 'ignore')

    def notify(self):
        # print self.full_parent_url()
        subject = 'Портал МИРТА: Требуется Ваше подтверждение.'
        text = '<html><p>Вы разместили комментарий на странице <a href="{}">{}</a>.</p>' +\
        '<p>Для активации комментария подтвердите его, перейдя по ссылке {}. </p>' +\
        '<p>Если данное уведомление пришло к Вам по ошибке, действий не требуется.</p>' +\
        '</html>'
        text = text.encode('utf-8', 'ignore').format(self.full_parent_url(), self.full_parent_url(), self.confirm_url())
        sender = 'mirta@mts.ru'
        to = self.commenter_email
        if ASYNC_NOTIFICATIONS:
            ntf.enqueue_notification(subject=subject, text=text, sender=sender, to=to)
        else:
            # to = [to]
            ntf.notify(subject=subject, text=text, sender=sender, to=to)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.confirmation_token = uuid.uuid4().hex
            while True:
                try:
                    super(Comment, self).save(*args, **kwargs)
                    if not self.is_active:
                        self.notify()
                    break
                except IntegrityError:
                    self.confirmation_token = uuid.uuid4().hex
        else:
            super(Comment, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at', 'id']