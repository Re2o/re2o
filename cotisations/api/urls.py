# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019 Arthur Grisel-Davy
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

"""Defines the URLs of the API for Cotisation

A custom router is used to register all the routes. That allows to register
all the URL patterns from the viewsets as a standard router but, the views
can also be register. That way a complete API root page presenting all URLs
can be generated automatically.
"""

from django.conf.urls import url, include

from . import views
from api.routers import AllViewsRouter

def add_to_router(router):
    router.register_viewset(r'cotisations/facture', views.FactureViewSet)
    router.register_viewset(r'cotisations/vente', views.VenteViewSet)
    router.register_viewset(r'cotisations/article', views.ArticleViewSet)
    router.register_viewset(r'cotisations/banque', views.BanqueViewSet)
    router.register_viewset(r'cotisations/paiement', views.PaiementViewSet)
    router.register_viewset(r'cotisations/cotisation', views.CotisationViewSet)
