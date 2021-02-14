# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018 Maël Kervella
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

from rest_framework import generics, viewsets

import cotisations.models as cotisations
import preferences.models as preferences

from . import serializers


class FactureViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Facture` objects."""

    queryset = cotisations.Facture.objects.all()
    serializer_class = serializers.FactureSerializer


class FactureViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Facture` objects."""

    queryset = cotisations.BaseInvoice.objects.all()
    serializer_class = serializers.BaseInvoiceSerializer


class VenteViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Vente` objects."""

    queryset = cotisations.Vente.objects.all()
    serializer_class = serializers.VenteSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Article` objects."""

    queryset = cotisations.Article.objects.all()
    serializer_class = serializers.ArticleSerializer


class BanqueViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Banque` objects."""

    queryset = cotisations.Banque.objects.all()
    serializer_class = serializers.BanqueSerializer


class PaiementViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Paiement` objects."""

    queryset = cotisations.Paiement.objects.all()
    serializer_class = serializers.PaiementSerializer


class CotisationViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Cotisation` objects."""

    queryset = cotisations.Cotisation.objects.all()
    serializer_class = serializers.CotisationSerializer


class ReminderView(generics.ListAPIView):
    """Output for users to remind an end of their subscription."""

    queryset = preferences.Reminder.objects.all()
    serializer_class = serializers.ReminderSerializer
