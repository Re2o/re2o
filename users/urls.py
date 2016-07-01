from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^new_user/$', views.new_user, name='users-new-user'),
    url(r'^edit_info/(?P<userid>[0-9]+)$', views.edit_info, name='users-edit-info'),
    url(r'^state/(?P<userid>[0-9]+)$', views.state, name='users-state'),
    url(r'^password/(?P<userid>[0-9]+)$', views.password, name='users-password'),
    url(r'^$', views.index, name='users-index'),
]


