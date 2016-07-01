from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^new_user/$', views.new_user, name='new_user'),
    url(r'^edit_info/(?P<userid>[0-9]+)$', views.edit_info, name='edit_info'),
]

