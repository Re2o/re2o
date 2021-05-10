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

from rest_framework import serializers

from tickets.models import Ticket, CommentTicket
from api.serializers import NamespacedHMSerializer


class TicketSerializer(NamespacedHMSerializer):
    """Serialize `tickets.models.Ticket` objects."""

    class Meta:
        model = Ticket
        fields = ("id", "title", "description", "email", "uuid")


class CommentTicketSerializer(NamespacedHMSerializer):
    uuid = serializers.UUIDField()

    class Meta:
        model = CommentTicket
        fields = ("comment", "uuid", "parent_ticket", "created_at", "created_by")
        read_only_fields = ("parent_ticket", "created_at", "created_by")
        extra_kwargs = {
            "uuid": {"write_only": True},
        }

    def create(self, validated_data):
        validated_data = {
            "comment": validated_data["comment"],
            "parent_ticket": Ticket.objects.get(uuid=validated_data["uuid"]),
            "created_by": validated_data["created_by"],
        }
        comment = CommentTicket(**validated_data)
        comment.save()
        return comment
