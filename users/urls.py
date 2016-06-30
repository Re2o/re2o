from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^new_user/$', views.new_user, name='new_user'),
]

