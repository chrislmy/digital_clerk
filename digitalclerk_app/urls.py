from django.conf.urls import url
from . import views

app_name = 'digitalclerk_app'

urlpatterns = [
    url(r'^dashboard$', views.dashboard, name='dashboard'),
    url(r'^office$', views.office, name='office'),
]