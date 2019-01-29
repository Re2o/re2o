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

"""Defines the views of the API

All views inherits the `rest_framework.views.APIview` to respect the
REST API requirements such as dealing with HTTP status code, format of
the response (JSON or other), the CSRF exempting, ...
"""

import datetime

from django.conf import settings
from django.db.models import Q
from rest_framework import viewsets, generics, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

import cotisations.models as cotisations
from re2o.utils import all_active_interfaces, all_has_access
from . import serializers
from api.pagination import PageSizedPagination
from api.permissions import ACLPermission


# COTISATIONS


class FactureViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Facture` objects.
    """
    queryset = cotisations.Facture.objects.all()
    serializer_class = serializers.FactureSerializer

class FactureViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Facture` objects.
    """
    queryset = cotisations.BaseInvoice.objects.all()
    serializer_class = serializers.BaseInvoiceSerializer


class VenteViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Vente` objects.
    """
    queryset = cotisations.Vente.objects.all()
    serializer_class = serializers.VenteSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Article` objects.
    """
    queryset = cotisations.Article.objects.all()
    serializer_class = serializers.ArticleSerializer


class BanqueViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Banque` objects.
    """
    queryset = cotisations.Banque.objects.all()
    serializer_class = serializers.BanqueSerializer


class PaiementViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Paiement` objects.
    """
    queryset = cotisations.Paiement.objects.all()
    serializer_class = serializers.PaiementSerializer


class CotisationViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Cotisation` objects.
    """
    queryset = cotisations.Cotisation.objects.all()
    serializer_class = serializers.CotisationSerializer
