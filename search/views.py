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

"""The views for the search app, responsible for finding the matches
Augustin lemesle, Gabriel Détraz, Goulven Kermarec, Maël Kervella
Gplv2"""


from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from users.models import User, Ban, Whitelist
from machines.models import Machine
from topologie.models import Port, Switch, Room
from cotisations.models import Facture
from preferences.models import GeneralOption
from search.forms import (
    SearchForm,
    SearchFormPlus,
    CHOICES_USER,
    CHOICES_AFF,
    initial_choices
)
from re2o.utils import SortTable


def is_int(variable):
    """ Check if the variable can be casted to an integer """

    try:
        int(variable)
    except ValueError:
        return False
    else:
        return True


def get_results(query, request, filters={}):
    """ Construct the correct filters to match differents fields of some models
    with the given query according to the given filters.
    The match field are either CharField or IntegerField that will be displayed
    on the results page (else, one might not see why a result has matched the
    query). IntegerField are matched against the query only if it can be casted
    to an int."""

    start = filters.get('s', None)
    end = filters.get('e', None)
    user_state = filters.get('u', initial_choices(CHOICES_USER))
    aff = filters.get('a', initial_choices(CHOICES_AFF))

    options, _ = GeneralOption.objects.get_or_create()
    max_result = options.search_display_page

    results = {
        'users_list': User.objects.none(),
        'machines_list': Machine.objects.none(),
        'factures_list': Facture.objects.none(),
        'bans_list': Ban.objects.none(),
        'whitelists_list': Whitelist.objects.none(),
        'rooms_list': Room.objects.none(),
        'switch_ports_list': Port.objects.none(),
        'switches_list': Switch.objects.none()
    }

    # Users
    if '0' in aff:
        filter_user_list = (
            Q(
                surname__icontains=query
            ) | Q(
                adherent__name__icontains=query
            ) | Q(
                pseudo__icontains=query
            ) | Q(
                club__room__name__icontains=query
            ) | Q(
                adherent__room__name__icontains=query
            )
        ) & Q(state__in=user_state)
        if not request.user.has_perms(('cableur',)):
            filter_user_list &= Q(id=request.user.id)
        results['users_list'] = User.objects.filter(filter_user_list)
        results['users_list'] = SortTable.sort(
            results['users_list'],
            request.GET.get('col'),
            request.GET.get('order'),
            SortTable.USERS_INDEX
        )

    # Machines
    if '1' in aff:
        filter_machine_list = Q(
            name__icontains=query
        ) | (
            Q(
                user__pseudo__icontains=query
            ) & Q(
                user__state__in=user_state
            )
        ) | Q(
            interface__domain__name__icontains=query
        ) | Q(
            interface__domain__related_domain__name__icontains=query
        ) | Q(
            interface__mac_address__icontains=query
        ) | Q(
            interface__ipv4__ipv4__icontains=query
        )
        if not request.user.has_perms(('cableur',)):
            filter_machine_list &= Q(user__id=request.user.id)
        results['machines_list'] = Machine.objects.filter(filter_machine_list)
        results['machines_list'] = SortTable.sort(
            results['machines_list'],
            request.GET.get('col'),
            request.GET.get('order'),
            SortTable.MACHINES_INDEX
        )

    # Factures
    if '2' in aff:
        filter_facture_list = Q(
            user__pseudo__icontains=query
        ) & Q(
            user__state__in=user_state
        )
        if start is not None:
            filter_facture_list &= Q(date__gte=start)
        if end is not None:
            filter_facture_list &= Q(date__lte=end)
        results['factures_list'] = Facture.objects.filter(filter_facture_list)
        results['factures_list'] = SortTable.sort(
            results['factures_list'],
            request.GET.get('col'),
            request.GET.get('order'),
            SortTable.COTISATIONS_INDEX
        )

    # Bans
    if '3' in aff:
        date_filter = (
            Q(
                user__pseudo__icontains=query
            ) & Q(
                user__state__in=user_state
            )
        ) | Q(
            raison__icontains=query
        )
        if start is not None:
            date_filter &= (
                Q(date_start__gte=start) & Q(date_end__gte=start)
            ) | (
                Q(date_start__lte=start) & Q(date_end__gte=start)
            ) | (
                Q(date_start__gte=start) & Q(date_end__lte=start)
            )
        if end is not None:
            date_filter &= (
                Q(date_start__lte=end) & Q(date_end__lte=end)
            ) | (
                Q(date_start__lte=end) & Q(date_end__gte=end)
            ) | (
                Q(date_start__gte=end) & Q(date_end__lte=end)
            )
        results['bans_list'] = Ban.objects.filter(date_filter)
        results['bans_list'] = SortTable.sort(
            results['bans_list'],
            request.GET.get('col'),
            request.GET.get('order'),
            SortTable.USERS_INDEX_BAN
        )

    # Whitelists
    if '4' in aff:
        date_filter = (
            Q(
                user__pseudo__icontains=query
            ) & Q(
                user__state__in=user_state
            )
        ) | Q(
            raison__icontains=query
        )
        if start is not None:
            date_filter &= (
                Q(date_start__gte=start) & Q(date_end__gte=start)
            ) | (
                Q(date_start__lte=start) & Q(date_end__gte=start)
            ) | (
                Q(date_start__gte=start) & Q(date_end__lte=start)
            )
        if end is not None:
            date_filter &= (
                Q(date_start__lte=end) & Q(date_end__lte=end)
            ) | (
                Q(date_start__lte=end) & Q(date_end__gte=end)
            ) | (
                Q(date_start__gte=end) & Q(date_end__lte=end)
            )
        results['whitelists_list'] = Whitelist.objects.filter(date_filter)
        results['whitelists_list'] = SortTable.sort(
            results['whitelists_list'],
            request.GET.get('col'),
            request.GET.get('order'),
            SortTable.USERS_INDEX_WHITE
        )

    # Rooms
    if '5' in aff and request.user.has_perms(('cableur',)):
        filter_rooms_list = Q(
            details__icontains=query
        ) | Q(
            name__icontains=query
        ) | Q(
            port__details=query
        )
        results['rooms_list'] = Room.objects.filter(filter_rooms_list)
        results['rooms_list'] = SortTable.sort(
            results['rooms_list'],
            request.GET.get('col'),
            request.GET.get('order'),
            SortTable.TOPOLOGIE_INDEX_ROOM
        )

    # Switch ports
    if '6' in aff and request.user.has_perms(('cableur',)):
        filter_ports_list = Q(
            room__name__icontains=query
        ) | Q(
            machine_interface__domain__name__icontains=query
        ) | Q(
            related__switch__switch_interface__domain__name__icontains=query
        ) | Q(
            radius__icontains=query
        ) | Q(
            vlan_force__name__icontains=query
        ) | Q(
            details__icontains=query
        )
        if is_int(query):
            filter_ports_list |= Q(
                port=query
            )
        results['switch_ports_list'] = Port.objects.filter(filter_ports_list)
        results['switch_ports_list'] = SortTable.sort(
            results['switch_ports_list'],
            request.GET.get('col'),
            request.GET.get('order'),
            SortTable.TOPOLOGIE_INDEX_PORT
        )

    # Switches
    if '7' in aff and request.user.has_perms(('cableur',)):
        filter_switches_list = Q(
            switch_interface__domain__name__icontains=query
        ) | Q(
            switch_interface__ipv4__ipv4__icontains=query
        ) | Q(
            location__icontains=query
        ) | Q(
            stack__name__icontains=query
        ) | Q(
            model__reference__icontains=query
        ) | Q(
            model__constructor__name__icontains=query
        ) | Q(
            details__icontains=query
        )
        if is_int(query):
            filter_switches_list |= Q(
                number=query
            ) | Q(
                stack_member_id=query
            )
        results['switches_list'] = Switch.objects.filter(filter_switches_list)
        results['switches_list'] = SortTable.sort(
            results['switches_list'],
            request.GET.get('col'),
            request.GET.get('order'),
            SortTable.TOPOLOGIE_INDEX
        )

    for name, val in results.items():
        results[name] = val.distinct()[:max_result]

    results.update({'max_result': max_result})
    results.update({'search_term': query})

    return results


@login_required
def search(request):
    """ La page de recherche standard """
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid():
        return render(
            request,
            'search/index.html',
            get_results(
                search_form.cleaned_data.get('q', ''),
                request,
                search_form.cleaned_data
            )
        )
    return render(request, 'search/search.html', {'search_form': search_form})


@login_required
def searchp(request):
    """ La page de recherche avancée """
    search_form = SearchFormPlus(request.GET or None)
    if search_form.is_valid():
        return render(
            request,
            'search/index.html',
            get_results(
                search_form.cleaned_data.get('q', ''),
                request,
                search_form.cleaned_data
            )
        )
    return render(request, 'search/search.html', {'search_form': search_form})
