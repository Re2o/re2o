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
    Interface,
    Machine,
    Vlan,
    MachineType,
    IpType,
    Extension,
    Domain,
    OuverturePortList,
    IpList
)

from re2o.mixins import AutocompleteViewMixin

from re2o.acl import (
    can_view_all,
)


class VlanAutocomplete(AutocompleteViewMixin):
    obj_type = Vlan


class MachineAutocomplete(AutocompleteViewMixin):
    obj_type = Machine


class MachineTypeAutocomplete(AutocompleteViewMixin):
    obj_type = MachineType


class IpTypeAutocomplete(AutocompleteViewMixin):
    obj_type = IpType


class ExtensionAutocomplete(AutocompleteViewMixin):
    obj_type = Extension 


class DomainAutocomplete(AutocompleteViewMixin):
    obj_type = Domain 


class OuverturePortListAutocomplete(AutocompleteViewMixin):
    obj_type = OuverturePortList 


class InterfaceAutocomplete(AutocompleteViewMixin):
    obj_type = Interface

    def get_queryset(self):
        qs = self.obj_type.objects.all()

        if self.q:
            qs = qs.filter(
                Q(domain__name__icontains=self.q)
                | Q(machine__name__icontains=self.q)
            )

        return qs


class IpListAutocomplete(AutocompleteViewMixin):
    obj_type = IpList

    def get_queryset(self):
        machine_type = self.forwarded.get('machine_type', None)
        qs = self.obj_type.objects.filter(interface__isnull=True)
        if machine_type:
            qs = qs.filter(ip_type__machinetype__id=machine_type)
        if self.q:
            qs = qs.filter(
                Q(ipv4__startswith=self.q)
            )

        return qs
