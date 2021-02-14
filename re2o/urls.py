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

from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from .settings_local import OPTIONNAL_APPS_RE2O
from .views import about_page, contact_page, handler404, handler500, index

# Admin site configuration
admin.site.index_title = _("Homepage")
admin.site.index_template = "admin/custom_index.html"

handler500 = handler500
handler404 = handler404

urlpatterns = [
    path("", index, name="index"),
    path("about", about_page, name="about"),
    path("contact", contact_page, name="contact"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("users/", include("users.urls", namespace="users")),
    path("search/", include("search.urls", namespace="search")),
    path("cotisations/", include("cotisations.urls", namespace="cotisations")),
    path("machines/", include("machines.urls", namespace="machines")),
    path("topologie/", include("topologie.urls", namespace="topologie")),
    path("logs/", include("logs.urls", namespace="logs")),
    path("preferences/", include("preferences.urls", namespace="preferences")),
    # Include contrib auth and contrib admin
    # manage/login/ is redirected to the non-admin login page
    path("", include("django.contrib.auth.urls")),
    path("admin/login/", RedirectView.as_view(pattern_name="login")),
    path("admin/", admin.site.urls),
]


urlpatterns += [
    path("{}/".format(app), include("{}.urls".format(app), namespace=app))
    for app in OPTIONNAL_APPS_RE2O
]

# Add debug_toolbar URLs if activated
if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
if "api" in settings.INSTALLED_APPS:
    urlpatterns += [path("api/", include("api.urls", namespace="api"))]
