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

from .models import Room, Dormitory, Building, Switch, PortProfile, Port, SwitchBay

from re2o.views import AutocompleteViewMixin, AutocompleteUnloggedViewMixin


class RoomAutocomplete(AutocompleteUnloggedViewMixin):
    obj_type = Room

    # Precision on search to add annotations so search behaves more like users expect it to
    def filter_results(self):
        # Suppose we have a dorm named Dorm, a building named B, and rooms from 001 - 999
        # Comments explain what we try to match
        self.query_set = self.query_set.annotate(
            full_name=Concat(
                "building__name", Value(" "), "name"
            ),  # Match when the user searches "B 001"
            full_name_stuck=Concat("building__name", "name"),  # Match "B001"
            dorm_name=Concat(
                "building__dormitory__name", Value(" "), "name"
            ),  # Match "Dorm 001"
            dorm_full_name=Concat(
                "building__dormitory__name",
                Value(" "),
                "building__name",
                Value(" "),
                "name",
            ),  # Match "Dorm B 001"
            dorm_full_colon_name=Concat(
                "building__dormitory__name",
                Value(" : "),
                "building__name",
                Value(" "),
                "name",
            ),  # Match "Dorm : B 001" (see Room's full_name property)
        ).all()

        if self.q:
            self.query_set = self.query_set.filter(
                Q(full_name__icontains=self.q)
                | Q(full_name_stuck__icontains=self.q)
                | Q(dorm_name__icontains=self.q)
                | Q(dorm_full_name__icontains=self.q)
                | Q(dorm_full_colon_name__icontains=self.q)
            )


class DormitoryAutocomplete(AutocompleteViewMixin):
    obj_type = Dormitory


class BuildingAutocomplete(AutocompleteViewMixin):
    obj_type = Building

    def filter_results(self):
        # We want to be able to filter by dorm so it's easier
        self.query_set = self.query_set.annotate(
            full_name=Concat("dormitory__name", Value(" "), "name"),
            full_name_colon=Concat("dormitory__name", Value(" : "), "name"),
        ).all()

        if self.q:
            self.query_set = self.query_set.filter(
                Q(full_name__icontains=self.q) | Q(full_name_colon__icontains=self.q)
            )


class SwitchAutocomplete(AutocompleteViewMixin):
    obj_type = Switch


class PortAutocomplete(AutocompleteViewMixin):
    obj_type = Port

    def filter_results(self):
        # We want to enter the switch name, not just the port number
        # Because we're concatenating a CharField and an Integer, we have to specify the output_field
        self.query_set = self.query_set.annotate(
            full_name=Concat(
                "switch__name", Value(" "), "port", output_field=CharField()
            ),
            full_name_stuck=Concat("switch__name", "port", output_field=CharField()),
            full_name_dash=Concat(
                "switch__name", Value(" - "), "port", output_field=CharField()
            ),
        ).all()

        if self.q:
            self.query_set = self.query_set.filter(
                Q(full_name__icontains=self.q)
                | Q(full_name_stuck__icontains=self.q)
                | Q(full_name_dash__icontains=self.q)
            )


class SwitchBayAutocomplete(AutocompleteViewMixin):
    obj_type = SwitchBay

    def filter_results(self):
        # See RoomAutocomplete.filter_results
        self.query_set = self.query_set.annotate(
            full_name=Concat(
                "building__name", Value(" "), "name"
            ),
            dorm_name=Concat(
                "building__dormitory__name", Value(" "), "name"
            ),
            dorm_full_name=Concat(
                "building__dormitory__name",
                Value(" "),
                "building__name",
                Value(" "),
                "name",
            ),
            dorm_full_colon_name=Concat(
                "building__dormitory__name",
                Value(" : "),
                "building__name",
                Value(" "),
                "name",
            ),
        ).all()

        if self.q:
            self.query_set = self.query_set.filter(
                Q(full_name__icontains=self.q)
                | Q(dorm_name__icontains=self.q)
                | Q(dorm_full_name__icontains=self.q)
                | Q(dorm_full_colon_name__icontains=self.q)
            )


class PortProfileAutocomplete(AutocompleteViewMixin):
    obj_type = PortProfile
