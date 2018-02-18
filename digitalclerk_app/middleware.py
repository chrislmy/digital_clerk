from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.deprecation import MiddlewareMixin

class AutoLoginRedicrect(MiddlewareMixin):
  def process_request(self, request):
    try:
        token = request.session['token_code']
        print(token)
        # If token is "logged_out"
        if (token == settings.SESSION_TOKEN_LOGGED_OUT):
            if request.path == reverse('digitalclerk_app:login_home'):
                return
            if request.path == reverse('digitalclerk_app:process_logout'):
                return HttpResponseRedirect('login_home')
            if request.path == reverse('digitalclerk_app:login_process'):
                request.session['token_code'] = settings.SESSION_TOKEN_LOGGING_IN
                return HttpResponseRedirect('login_process')
            if request.path == reverse('digitalclerk_app:admin_index'):
                return;
            if request.path == reverse('digitalclerk_app:login_process_admin'):
                return;
            if request.path == reverse('digitalclerk_app:process_logout_admin'):
                return;
            if not request.path == reverse('digitalclerk_app:login_process'):
                request.session['token_code'] = settings.SESSION_TOKEN_LOGGING_IN
                return HttpResponseRedirect('login_process')
        # If token is "logging_in". This happens if users do not complete the log in
        if (token == settings.SESSION_TOKEN_LOGGING_IN):
            if request.path == reverse('digitalclerk_app:login_home'):
                request.session['token_code'] = settings.SESSION_TOKEN_LOGGED_OUT
                return
            if request.path == reverse('digitalclerk_app:oauth_callback'):
                return
            if request.path == reverse('digitalclerk_app:login_process'):
                return;
            if request.path == reverse('digitalclerk_app:admin_index'):
                return;
            if request.path == reverse('digitalclerk_app:login_process_admin'):
                return;
            if request.path == reverse('digitalclerk_app:process_logout_admin'):
                return;
            if not request.path == reverse('digitalclerk_app:login_process'):
                request.session['token_code'] = settings.SESSION_TOKEN_LOGGING_IN
                return HttpResponseRedirect(reverse('digitalclerk_app:login_process'))
        return
    except KeyError:
        request.session['token_code'] = settings.SESSION_TOKEN_LOGGED_OUT
        return HttpResponseRedirect('login_home')