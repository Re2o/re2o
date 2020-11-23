# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
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
# Goulven Kermarec, Gabriel Détraz, Lemesle Augustin
# Gplv2

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.forms import modelformset_factory
from django.db.models import Q
from re2o.views import form
from re2o.utils import all_has_access, all_adherent

from re2o.base import re2o_paginator, SortTable

from re2o.acl import can_view, can_view_all, can_edit, can_create

from preferences.models import GeneralOption, AssoOption

from .forms import DormitoryForm

from .preferences.models import MultiopOption

from topologie.models import Room, Dormitory


def display_rooms_connection(request, dormitory=None):
    """View used to display an overview of the rooms' connection state.

    Args:
        request: django request.
        dormitory: Dormitory, the dormitory used to filter rooms. If no
            dormitory is given, all rooms are displayed (default: None).
    """
    room_list = Room.objects.select_related("building__dormitory").filter(
        building__dormitory__in=MultiopOption.get_cached_value("enabled_dorm").all()
    ).order_by("building_dormitory", "port")
    if dormitory:
        room_list = room_list.filter(building__dormitory=dormitory)
    room_list = SortTable.sort(
        room_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_ROOM,
    )
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    room_list = re2o_paginator(request, room_list, pagination_number)
    asso_name = AssoOption.get_cached_value("pseudo")
    return render(
        request,
        "multi_op/index_room_state.html",
        {
            "room_list": room_list,
            "asso_name": asso_name,
        },
    )


@login_required
@can_view_all(Room)
def aff_state_global(request):
    """View used to display the connection state of all rooms."""
    return display_rooms_connection(request)


@login_required
@can_view(Dormitory)
def aff_state_dormitory(request, dormitory, dormitoryid):
    """View used to display the connection state of the rooms in the given
    dormitory.

    Args:
        request: django request.
        dormitory: Dormitory, the dormitory used to filter rooms.
        dormitoryid: int, the id of the dormitory.
    """
    return display_rooms_connection(dormitory=dormitory)


@login_required
@can_view_all(Room)
def aff_pending_connection(request):
    """View used to display rooms pending connection to the organisation's
    network.
    """
    room_list = (
        Room.objects.select_related("building__dormitory")
        .filter(port__isnull=True)
        .filter(adherent__in=all_has_access())
        .filter(building__dormitory__in=MultiopOption.get_cached_value("enabled_dorm").all())
        .order_by("building_dormitory", "port")
    )
    dormitory_form = DormitoryForm(request.POST or None)
    if dormitory_form.is_valid():
        room_list = room_list.filter(
            building__dormitory__in=dormitory_form.cleaned_data["dormitory"]
        )
    room_list = SortTable.sort(
        room_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_ROOM,
    )
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    room_list = re2o_paginator(request, room_list, pagination_number)
    asso_name = AssoOption.get_cached_value("pseudo")
    return render(
        request,
        "multi_op/index_room_state.html",
        {
            "room_list": room_list,
            "dormitory_form": dormitory_form,
            "asso_name": asso_name,
        },
    )


@login_required
@can_view_all(Room)
def aff_pending_disconnection(request):
    """View used to display rooms pending disconnection from the organisation's
    network.
    """
    room_list = (
        Room.objects.select_related("building__dormitory")
        .filter(port__isnull=False)
        .exclude(Q(adherent__in=all_has_access()) | Q(adherent__in=all_adherent()))
        .filter(building__dormitory__in=MultiopOption.get_cached_value("enabled_dorm").all())
        .order_by("building_dormitory", "port")
    )
    dormitory_form = DormitoryForm(request.POST or None)
    if dormitory_form.is_valid():
        room_list = room_list.filter(
            building__dormitory__in=dormitory_form.cleaned_data["dormitory"]
        )
    room_list = SortTable.sort(
        room_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.TOPOLOGIE_INDEX_ROOM,
    )
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    room_list = re2o_paginator(request, room_list, pagination_number)
    asso_name = AssoOption.get_cached_value("pseudo")
    return render(
        request,
        "multi_op/index_room_state.html",
        {
            "room_list": room_list,
            "dormitory_form": dormitory_form,
            "asso_name": asso_name,
        },
    )


@login_required
@can_edit(Room)
def disconnect_room(request, room, roomid):
    """View used to disconnect a room.

    Args:
        request: django request.
        room: Room, the room to be disconnected.
        roomid: int, the id of the room.
    """
    room.port_set.clear()
    room.save()
    messages.success(request, _("The room %s was disconnected.") % room)
    return redirect(reverse("multi_op:aff-pending-disconnection"))


def navbar_user():
    """View used to display a link to manage operators in the navbar (in the
    dropdown menu Topology).
    """
    return ("topologie", render_to_string("multi_op/navbar.html"))
