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

from .models import ( 
    User,
    Ban,
    Whitelist,
    School,
    ListRight,
    Request,
    ServiceUser,
    Adherent,
    Club,
    ListShell,
    EMailAddress,
)

from re2o.mixins import AutocompleteViewMixin

from re2o.acl import (
    can_view_all,
)

from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat

#@can_view_all(School)
class SchoolAutocomplete(AutocompleteViewMixin):
    obj_type = School

#@can_view_all(User)
class UserAutocomplete(AutocompleteViewMixin):
    obj_type = User
    # Override get_queryset to add annotations so search behaves more like users expect it to
    def get_queryset(self):
        # Comments explain what we try to match
        qs = self.obj_type.objects.annotate(
            full_name=Concat("adherent__name", Value(" "), "surname"),  # Match when the user searches "Toto Passoir"
            full_name_reverse=Concat("surname", Value(" "), "adherent__name"),  # Match when the user searches "Passoir Toto"
        ).all()

        if self.q:
            qs = qs.filter(
                Q(pseudo__icontains=self.q)
                | Q(full_name__icontains=self.q)
                | Q(full_name_reverse__icontains=self.q)
            )

        return qs

#@can_view_all(Adherent)
class AdherentAutocomplete(AutocompleteViewMixin):
    obj_type = Adherent

#@can_view_all(Club)
class ClubAutocomplete(AutocompleteViewMixin):
    obj_type = Club

class ShellAutocomplete(AutocompleteViewMixin):
    obj_type = ListShell
    query_filter = "shell__icontains"
