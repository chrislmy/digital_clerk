from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.deprecation import MiddlewareMixin

class AutoLoginRedicrect(MiddlewareMixin):
  def process_request(self, request):
    try:
        token = request.session['token_code']
        if token == settings.SESSION_TOKEN_LOGGED_OUT:
            if request.path == reverse('digitalclerk_app:login_home'):
                return 
            if request.path == reverse('digitalclerk_app:login_process'):
                request.session['token_code'] = settings.SESSION_TOKEN_LOGGING_IN
                return HttpResponseRedirect('login_process')
            if not request.path == reverse('digitalclerk_app:login_process'):
                request.session['token_code'] = settings.SESSION_TOKEN_LOGGING_IN
                return HttpResponseRedirect('login_process')
        return
    except KeyError:
        request.session['token_code'] = "logged_out"
        return HttpResponseRedirect('login_home')