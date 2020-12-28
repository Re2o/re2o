# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017-2020  Gabriel Détraz
# Copyright © 2017-2020  Jean-Romain Garnier
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

# App de gestion des users pour re2o
# Lara Kermarec, Gabriel Détraz, Lemesle Augustin
# Gplv2
"""
Django views autocomplete view

Here are defined the autocomplete class based view.

"""
from __future__ import unicode_literals

from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat

from .models import (
    Room,
    Dormitory,
    Building,
    Switch,
    PortProfile,
    Port,
    SwitchBay,
)

from re2o.mixins import AutocompleteViewMixin

from re2o.acl import (
    can_view_all,
)


#@can_view_all(School)
class RoomAutocomplete(AutocompleteViewMixin):
    obj_type = Room

    # Override get_queryset to add annotations so search behaves more like users expect it to
    def get_queryset(self):
        # Suppose we have a dorm named Dorm, a building name B, and rooms from 001 - 999
        # Comments explain what we try to match
        qs = self.obj_type.objects.annotate(
            full_name=Concat("building__name", Value(" "), "name"),  # Match when the user searches "B 001"
            full_name_stuck=Concat("building__name", "name"),  # Match "B001"
            dorm_name=Concat("building__dormitory__name", Value(" "), "name"),  # Match "Dorm 001"
            dorm_full_name=Concat("building__dormitory__name", Value(" "), "building__name", Value(" "), "name"),  # Match "Dorm B 001"
            dorm_full_colon_name=Concat("building__dormitory__name", Value(" : "), "building__name", Value(" "), "name"),  # Match "Dorm : B 001" (see Room's full_name property)
        ).all()

        if self.q:
            qs = qs.filter(
                Q(full_name__icontains=self.q)
                | Q(full_name_stuck__icontains=self.q)
                | Q(dorm_name__icontains=self.q)
                | Q(dorm_full_name__icontains=self.q)
                | Q(dorm_full_colon_name__icontains=self.q)
            )

        return qs


#@can_view_all(Dormitory)
class DormitoryAutocomplete(AutocompleteViewMixin):
    obj_type = Dormitory


#@can_view_all(Building)
class BuildingAutocomplete(AutocompleteViewMixin):
    obj_type = Building

    def get_queryset(self):
        # We want to be able to filter by dorm so it's easier
        qs = self.obj_type.objects.annotate(
            full_name=Concat("dormitory__name", Value(" "), "name"),
            full_name_colon=Concat("dormitory__name", Value(" : "), "name"),
        ).all()

        if self.q:
            qs = qs.filter(
                Q(full_name__icontains=self.q)
                | Q(full_name_colon__icontains=self.q)
            )

        return qs

class SwitchAutocomplete(AutocompleteViewMixin):
    obj_type = Switch


class PortAutocomplete(AutocompleteViewMixin):
    obj_type = Port

    def get_queryset(self):
        # We want to enter the switch name, not just the port number
        # Because we're concatenating a CharField and an Integer, we have to sepcify the output_field
        qs = self.obj_type.objects.annotate(
            full_name=Concat("switch__name", Value(" "), "port", output_field=CharField()),
            full_name_stuck=Concat("switch__name", "port", output_field=CharField()),
            full_name_dash=Concat("switch__name", Value(" - "), "port", output_field=CharField()),
        ).all()

        if self.q:
            qs = qs.filter(
                Q(full_name__icontains=self.q)
                | Q(full_name_stuck__icontains=self.q)
                | Q(full_name_dash__icontains=self.q)
            )

        return qs


class SwitchBayAutocomplete(AutocompleteViewMixin):
    obj_type = SwitchBay

    def get_queryset(self):
        # Comments explain what we try to match
        qs = self.obj_type.objects.annotate(
            full_name=Concat("building__name", Value(" "), "name"),  # Match when the user searches ""
            dorm_name=Concat("building__dormitory__name", Value(" "), "name"),  # Match "Dorm Local Sud"
            dorm_full_name=Concat("building__dormitory__name", Value(" "), "building__name", Value(" "), "name"),  # Match "Dorm J Local Sud"
        ).all()

        if self.q:
            qs = qs.filter(
                Q(full_name__icontains=self.q)
                | Q(dorm_name__icontains=self.q)
                | Q(dorm_full_name__icontains=self.q)
            )

        return qs


class PortProfileAutocomplete(AutocompleteViewMixin):
    obj_type = PortProfile
