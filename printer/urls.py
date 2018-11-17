# -*- coding: utf-8 -*-
"""printer.urls
The defined URLs for the printer app
Author : Maxime Bombar <bombar@crans.org>.
Date : 29/06/2018
"""
from __future__ import unicode_literals

from django.conf.urls import url

import re2o
from . import views

urlpatterns = [
    url(r'^new_job/$', views.new_job, name="new-job"),
    url(r'^print_job/(?P<printoperationid>[0-9]+)$', views.print_job, name='print-job'),
    url(r'^index_jobs/$', views.index_jobs, name="index-jobs"),
    url(r'^index_digicodes/$', views.index_digicodes, name="index-digicodes"),
    url(r'^print_job_again/(?P<jobwithoptionsid>[0-9]+)$', views.print_job_again, name='print-job-again'),
    url(r'^create_digicode/', views.create_code, name='create-digicode'),


]
