# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
# Copyright © 2017  Augustin Lemesle
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""re2o URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home)
    3. Optional: Add a custom name for this URL:
         url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view())
    3. Optional: Add a custom name for this URL:
         url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
    2. Optional: Add a custom namespace for all URL using this urlpatterns:
         url(r'^blog/', include('blog.urls'), namespace='blog')
"""
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from .settings_local import OPTIONNAL_APPS_RE2O

from .views import index, about_page, contact_page

# Admin site configuration
admin.site.index_title = _("Homepage")
admin.site.index_template = "admin/custom_index.html"

handler500 = "re2o.views.handler500"
handler404 = "re2o.views.handler404"

urlpatterns = [
    url(r"^$", index, name="index"),
    url(r"^about/$", about_page, name="about"),
    url(r"^contact/$", contact_page, name="contact"),
    url(r"^i18n/", include("django.conf.urls.i18n")),
    url(r"^users/", include("users.urls", namespace="users")),
    url(r"^search/", include("search.urls", namespace="search")),
    url(r"^cotisations/", include("cotisations.urls", namespace="cotisations")),
    url(r"^machines/", include("machines.urls", namespace="machines")),
    url(r"^topologie/", include("topologie.urls", namespace="topologie")),
    url(r"^logs/", include("logs.urls", namespace="logs")),
    url(r"^preferences/", include("preferences.urls", namespace="preferences")),
    # Include contrib auth and contrib admin
    # manage/login/ is redirected to the non-admin login page
    url(r"^", include("django.contrib.auth.urls")),
    url(r"^admin/login/$", RedirectView.as_view(pattern_name="login")),
    url(r"^admin/", include(admin.site.urls)),
]


urlpatterns += [
    url(r"^{}/".format(app), include("{}.urls".format(app), namespace=app))
    for app in OPTIONNAL_APPS_RE2O
]

# Add debug_toolbar URLs if activated
if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [url(r"^__debug__/", include(debug_toolbar.urls))]
if "api" in settings.INSTALLED_APPS:
    urlpatterns += [url(r"^api/", include("api.urls", namespace="api"))]
