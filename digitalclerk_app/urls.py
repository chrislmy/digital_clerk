from django.conf.urls import url
from . import views

app_name = 'digitalclerk_app'

urlpatterns = [
    url(r'^dashboard$', views.dashboard, name='dashboard'),
    url(r'^admin_index$', views.admin_index, name='admin_index'),
    url(r'^dashboard/module_details/(?P<module_code>[0-9A-Za-z]+)$', views.module_details, name='module_details'),
    url(r'^add_office_hour$', views.add_office_hour, name='add_office_hour'),
    url(r'^edit_office_hour$', views.edit_office_hour, name='edit_office_hour')
]