# -*- coding: utf-8 -*-


from django.shortcuts import render, get_object_or_404, redirect
from django import forms

# from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget

from .models import Comment
from portal.views import error

# Create your views here.


class AddCommentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(AddCommentForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control input-sm '
            # visible.field.widget.attrs['class'] = 'form-control '
        self.fields['body'].label = False
        self.fields['parent_url'].label = False

    commenter_email = forms.EmailField(label='Ваш e-mail@mts.ru')
    commenter_name = forms.CharField(label='Ваше имя', max_length=250)
    body = forms.CharField(label='', label_suffix='', max_length=2000,
                          widget=CKEditorWidget(config_name='comment'))
    parent_url = forms.CharField(label='', label_suffix='', max_length=2000, widget=forms.HiddenInput)


def add_comment(request):
    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            # print 'valid!'
            cmnt = Comment(commenter_email=form.cleaned_data['commenter_email'],
                           commenter_name=form.cleaned_data['commenter_name'],
                           body=form.cleaned_data['body'],
                           parent_url=form.cleaned_data['parent_url'],
                        )
            cmnt.save()
            fresh_comments_str = ','.join(request.get_signed_cookie('fresh_comments', '').split(',')
                                                         + [cmnt.confirmation_token])
            # if request.user.is_authenticated:
            #     request.session['fresh_comments'] = fresh_comments_str
            #     response = redirect(form.cleaned_data['parent_url'])
            # else:
            response = redirect(form.cleaned_data['parent_url'])
            response.set_signed_cookie('fresh_comments', fresh_comments_str, max_age=86400)
            return response

    return error(request, 'Что-то пошло не так.')


class EditCommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EditCommentForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control input-sm'
        for key in list(self.fields.keys()):
            self.fields[key].widget.attrs['id'] = '{}_{}'.format(key, self.instance.pk)

    class Meta:
        model = Comment
        fields = ['commenter_name', 'body']


def edit_comment(request, id):
    try:
        id = int(id)
    except ValueError:
        return error(request, 'Указан неверный id комментария. Редактирование невозможно.')
    instance = get_object_or_404(Comment, pk=id)
    if request.method == 'POST':
        form = EditCommentForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(instance.parent_url)

    return error(request, 'Что-то пошло не так.')


def confirm(request, token):

    # qry = request.GET.urlencode()
    # if qry:
    #     qry = '?' + qry

    cmnt = get_object_or_404(Comment, confirmation_token=token)
    if cmnt:
        cmnt.is_active = True
        cmnt.save()

    return redirect(cmnt.parent_url)

