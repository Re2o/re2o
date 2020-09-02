# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2020 Mineau Jean-Marie
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

from re2o.utils import all_has_access
from . import serializers
import topologie.models as topologie

class PendingConnectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Expose list and detail of `topologie.models.Room` object
       waiting to be connected.
    """

    queryset = (
        topologie.Room.objects.select_related("building__dormitory")
        .filter(port__isnull=True)
        .filter(adherent__in=all_has_access())
        .order_by("building_dormitory", "port")
    )
    serializer_class = serializers.RoomSerializer
