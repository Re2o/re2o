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

from django.db.models import CharField, Q, Value
from django.db.models.functions import Concat

from re2o.views import AutocompleteLoggedOutViewMixin, AutocompleteViewMixin

from .models import Adherent, Club, ListShell, School, User


class SchoolAutocomplete(AutocompleteLoggedOutViewMixin):
    obj_type = School


class UserAutocomplete(AutocompleteViewMixin):
    obj_type = User

    # Precision on search to add annotations so search behaves more like users expect it to
    def filter_results(self):
        # Comments explain what we try to match
        self.query_set = self.query_set.annotate(
            full_name=Concat(
                "adherent__name", Value(" "), "surname"
            ),  # Match when the user searches "Toto Passoir"
            full_name_reverse=Concat(
                "surname", Value(" "), "adherent__name"
            ),  # Match when the user searches "Passoir Toto"
        ).all()

        if self.q:
            self.query_set = self.query_set.filter(
                Q(pseudo__icontains=self.q)
                | Q(full_name__icontains=self.q)
                | Q(full_name_reverse__icontains=self.q)
            )


class AdherentAutocomplete(AutocompleteViewMixin):
    obj_type = Adherent

    # Precision on search to add annotations so search behaves more like users expect it to
    def filter_results(self):
        # Comments explain what we try to match
        self.query_set = self.query_set.annotate(
            full_name=Concat(
                "name", Value(" "), "surname"
            ),  # Match when the user searches "Toto Passoir"
            full_name_reverse=Concat(
                "surname", Value(" "), "name"
            ),  # Match when the user searches "Passoir Toto"
        ).all()

        if self.q:
            self.query_set = self.query_set.filter(
                Q(pseudo__icontains=self.q)
                | Q(full_name__icontains=self.q)
                | Q(full_name_reverse__icontains=self.q)
            )


class ClubAutocomplete(AutocompleteViewMixin):
    obj_type = Club


class ShellAutocomplete(AutocompleteViewMixin):
    obj_type = ListShell
    query_filter = "shell__icontains"
