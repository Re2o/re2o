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

from rest_framework import viewsets

from tickets.models import Ticket, CommentTicket
from api.permissions import ACLPermission

from . import serializers


class TicketsViewSet(viewsets.ModelViewSet):

    permission_classes = (ACLPermission,)
    perms_map = {
        "GET": [Ticket.can_view_all],
        "POST": [],
    }
    serializer_class = serializers.TicketSerializer
    queryset = Ticket.objects.all()


class CommentTicketViewSet(viewsets.ModelViewSet):
    permission_classes = (ACLPermission,)
    perms_map = {
        "GET": [Ticket.can_view_all],
        "POST": [],
    }
    serializer_class = serializers.CommentTicketSerializer
    queryset = CommentTicket.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
