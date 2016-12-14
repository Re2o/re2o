from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^new_user/$', views.new_user, name='new-user'),
    url(r'^edit_info/(?P<userid>[0-9]+)$', views.edit_info, name='edit-info'),
    url(r'^state/(?P<userid>[0-9]+)$', views.state, name='state'),
    url(r'^password/(?P<userid>[0-9]+)$', views.password, name='password'),
    url(r'^add_ban/(?P<userid>[0-9]+)$', views.add_ban, name='add-ban'),
    url(r'^edit_ban/(?P<banid>[0-9]+)$', views.edit_ban, name='edit-ban'),
    url(r'^add_whitelist/(?P<userid>[0-9]+)$', views.add_whitelist, name='add-whitelist'),
    url(r'^edit_whitelist/(?P<whitelistid>[0-9]+)$', views.edit_whitelist, name='edit-whitelist'),
    url(r'^add_right/(?P<userid>[0-9]+)$', views.add_right, name='add-right'),
    url(r'^del_right/$', views.del_right, name='del-right'),
    url(r'^add_school/$', views.add_school, name='add-school'),
    url(r'^edit_school/(?P<schoolid>[0-9]+)$', views.edit_school, name='edit-school'),
    url(r'^del_school/$', views.del_school, name='del-school'),
    url(r'^add_listright/$', views.add_listright, name='add-listright'),
    url(r'^edit_listright/(?P<listrightid>[0-9]+)$', views.edit_listright, name='edit-listright'),
    url(r'^del_listright/$', views.del_listright, name='del-listright'),
    url(r'^profil/(?P<userid>[0-9]+)$', views.profil, name='profil'),
    url(r'^index_ban/$', views.index_ban, name='index-ban'),
    url(r'^index_white/$', views.index_white, name='index-white'),
    url(r'^index_school/$', views.index_school, name='index-school'),
    url(r'^index_listright/$', views.index_listright, name='index-listright'),
    url(r'^mon_profil/$', views.mon_profil, name='mon-profil'),
    url(r'^process/(?P<token>[a-z0-9]{32})/$', views.process, name='process'),
    url(r'^reset_password/$', views.reset_password, name='reset-password'),
    url(r'^history/(?P<object>user)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>ban)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>whitelist)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>school)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>listright)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^$', views.index, name='index'),
]


