from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^revert_action/(?P<revision_id>[0-9]+)$', views.revert_action, name='revert-action'),
    url(r'^stats_models/$', views.stats_models, name='stats-models'),
]
