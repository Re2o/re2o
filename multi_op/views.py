# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
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

from re2o.base import (
    re2o_paginator,
    SortTable,
)

from re2o.acl import(
    can_view,
    can_view_all,
    can_edit,
    can_create,
)

from preferences.models import GeneralOption

from .forms import DormitoryForm

from .preferences.models import(
    Preferences,
)

from topologie.models import Room, Dormitory

from .preferences.forms import (
    EditPreferencesForm,
)


def display_rooms_connection(request, dormitory=None):
    """View to display global state of connection state"""
    room_list = Room.objects.select_related('building__dormitory').order_by('building_dormitory', 'port')
    if dormitory:
        room_list = room_list.filter(building__dormitory=dormitory)
    room_list = SortTable.sort(
        room_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_ROOM
    )
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    room_list = re2o_paginator(request, room_list, pagination_number)
    return render(
        request,
        'multi_op/index_room_state.html',
        {'room_list': room_list}
    )


@login_required
@can_view_all(Room)
def aff_state_global(request):
    return display_rooms_connection(request)


@login_required
@can_view(Dormitory)
def aff_state_dormitory(request, dormitory, dormitoryid):
    return display_rooms_connection(dormitory=dormitory)


@login_required
@can_view_all(Room)
def aff_pending_connection(request):
    """Aff pending Rooms to connect on our network"""
    room_list = Room.objects.select_related('building__dormitory').filter(port__isnull=True).filter(adherent__in=all_has_access()).order_by('building_dormitory', 'port')
    dormitory_form = DormitoryForm(request.POST or None)
    if dormitory_form.is_valid():
        room_list = room_list.filter(building__dormitory__in=dormitory_form.cleaned_data['dormitory'])
    room_list = SortTable.sort(
        room_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_ROOM
    )
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    room_list = re2o_paginator(request, room_list, pagination_number)
    return render(
        request,
        'multi_op/index_room_state.html',
        {'room_list': room_list, 'dormitory_form': dormitory_form}
    )


@login_required
@can_view_all(Room)
def aff_pending_disconnection(request):
    """Aff pending Rooms to disconnect from our network"""
    room_list = Room.objects.select_related('building__dormitory').filter(port__isnull=False).exclude(Q(adherent__in=all_has_access()) | Q(adherent__in=all_adherent())).order_by('building_dormitory', 'port')
    dormitory_form = DormitoryForm(request.POST or None)
    if dormitory_form.is_valid():
        room_list = room_list.filter(building__dormitory__in=dormitory_form.cleaned_data['dormitory'])
    room_list = SortTable.sort(
        room_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.TOPOLOGIE_INDEX_ROOM
    )
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    room_list = re2o_paginator(request, room_list, pagination_number)
    return render(
        request,
        'multi_op/index_room_state.html',
        {'room_list': room_list, 'dormitory_form': dormitory_form}
    )


@login_required
@can_edit(Room)
def disconnect_room(request, room, roomid):
    """Action of disconnecting a room"""
    room.port_set.clear()
    room.save()
    messages.success(request,'Room %s disconnected' % room)
    return redirect(reverse(
        'multi_op:aff-pending-disconnection'
    ))


def navbar_user():
    """View to display the app in user's dropdown in the navbar"""
    return ('topologie', render_to_string('multi_op/navbar.html'))




