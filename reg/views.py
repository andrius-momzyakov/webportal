from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.views import PasswordContextMixin
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.views.generic.edit import FormView
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse_lazy
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import update_session_auth_hash
from django.utils.translation import ugettext_lazy as _


from utils.portal_decorators import portalctx

# Create your views here.


class mLoginView(LoginView):

    @portalctx
    def get_context_data(self, **kwargs):

        opt_context = kwargs['context'] if 'context' in kwargs else {}

        context = super(LoginView, self).get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        context.update({
            self.redirect_field_name: self.get_redirect_url(),
            'site': current_site,
            'site_name': current_site.name,
        })
        if self.extra_context is not None:
            context.update(self.extra_context)
        if opt_context:
            context.update(opt_context)
        return context


class mPasswordContextMixin(PasswordContextMixin):

    @portalctx
    def get_context_data(self, **kwargs):

        opt_context = kwargs['context'] if 'context' in kwargs else {}

        context = super(PasswordContextMixin, self).get_context_data(**kwargs)
        context['title'] = self.title
        if self.extra_context is not None:
            context.update(self.extra_context)
        if opt_context:
            context.update(opt_context)
        return context


class mPasswordChangeDoneView(mPasswordContextMixin, TemplateView):
    template_name = 'registration/password_change_done.html'
    title = _('Password change successful')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(mPasswordChangeDoneView, self).dispatch(*args, **kwargs)


class mPasswordChangeView(mPasswordContextMixin, FormView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'registration/password_change_form.html'
    title = _('Password change')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(mPasswordChangeView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(mPasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        return super(mPasswordChangeView, self).form_valid(form)

