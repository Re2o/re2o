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
from users.models import User, Adherent, Club, Ban, Whitelist
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


def finish_results(results, col, order):
    """Sort the results by applying filters and then limit them to the
    number of max results. Finally add the info of the nmax number of results
    to the dict"""

    results['users'] = SortTable.sort(
        results['users'],
        col,
        order,
        SortTable.USERS_INDEX
    )
    results['machines'] = SortTable.sort(
        results['machines'],
        col,
        order,
        SortTable.MACHINES_INDEX
    )
    results['factures'] = SortTable.sort(
        results['factures'],
        col,
        order,
        SortTable.COTISATIONS_INDEX
    )
    results['bans'] = SortTable.sort(
        results['bans'],
        col,
        order,
        SortTable.USERS_INDEX_BAN
    )
    results['whitelists'] = SortTable.sort(
        results['whitelists'],
        col,
        order,
        SortTable.USERS_INDEX_WHITE
    )
    results['rooms'] = SortTable.sort(
        results['rooms'],
        col,
        order,
        SortTable.TOPOLOGIE_INDEX_ROOM
    )
    results['ports'] = SortTable.sort(
        results['ports'],
        col,
        order,
        SortTable.TOPOLOGIE_INDEX_PORT
    )
    results['switches'] = SortTable.sort(
        results['switches'],
        col,
        order,
        SortTable.TOPOLOGIE_INDEX
    )

    max_result = GeneralOption.get_cached_value('search_display_page')
    for name, val in results.items():
        results[name] = val.distinct()[:max_result]
    results.update({'max_result': max_result})

    return results


def search_single_word(word, filters, user,
                       start, end, user_state, aff):
    """ Construct the correct filters to match differents fields of some models
    with the given query according to the given filters.
    The match field are either CharField or IntegerField that will be displayed
    on the results page (else, one might not see why a result has matched the
    query). IntegerField are matched against the query only if it can be casted
    to an int."""

    # Users
    if '0' in aff:
        filter_users = (
            Q(
                surname__icontains=word
            ) | Q(
                pseudo__icontains=word
            ) | Q(
                room__name__icontains=word
            ) | Q(
                room__name__icontains=word
            )
        ) & Q(state__in=user_state)
        if not User.can_view_all(user)[0]:
            filter_users &= Q(id=user.id)
        filter_clubs = filter_users
        filter_users |= Q(name__icontains=word)       
        filters['users'] |= filter_users
        filters['clubs'] |= filter_clubs

    # Machines
    if '1' in aff:
        filter_machines = Q(
            name__icontains=word
        ) | (
            Q(
                user__pseudo__icontains=word
            ) & Q(
                user__state__in=user_state
            )
        ) | Q(
            interface__domain__name__icontains=word
        ) | Q(
            interface__domain__related_domain__name__icontains=word
        ) | Q(
            interface__mac_address__icontains=word
        ) | Q(
            interface__ipv4__ipv4__icontains=word
        )
        if not Machine.can_view_all(user)[0]:
            filter_machines &= Q(user__id=user.id)
        filters['machines'] |= filter_machines

    # Factures
    if '2' in aff:
        filter_factures = Q(
            user__pseudo__icontains=word
        ) & Q(
            user__state__in=user_state
        )
        if start is not None:
            filter_factures &= Q(date__gte=start)
        if end is not None:
            filter_factures &= Q(date__lte=end)
        filters['factures'] |= filter_factures

    # Bans
    if '3' in aff:
        filter_bans = (
            Q(
                user__pseudo__icontains=word
            ) & Q(
                user__state__in=user_state
            )
        ) | Q(
            raison__icontains=word
        )
        if start is not None:
            filter_bans &= (
                Q(date_start__gte=start) & Q(date_end__gte=start)
            ) | (
                Q(date_start__lte=start) & Q(date_end__gte=start)
            ) | (
                Q(date_start__gte=start) & Q(date_end__lte=start)
            )
        if end is not None:
            filter_bans &= (
                Q(date_start__lte=end) & Q(date_end__lte=end)
            ) | (
                Q(date_start__lte=end) & Q(date_end__gte=end)
            ) | (
                Q(date_start__gte=end) & Q(date_end__lte=end)
            )
        filters['bans'] |= filter_bans

    # Whitelists
    if '4' in aff:
        filter_whitelists = (
            Q(
                user__pseudo__icontains=word
            ) & Q(
                user__state__in=user_state
            )
        ) | Q(
            raison__icontains=word
        )
        if start is not None:
            filter_whitelists &= (
                Q(date_start__gte=start) & Q(date_end__gte=start)
            ) | (
                Q(date_start__lte=start) & Q(date_end__gte=start)
            ) | (
                Q(date_start__gte=start) & Q(date_end__lte=start)
            )
        if end is not None:
            filter_whitelists &= (
                Q(date_start__lte=end) & Q(date_end__lte=end)
            ) | (
                Q(date_start__lte=end) & Q(date_end__gte=end)
            ) | (
                Q(date_start__gte=end) & Q(date_end__lte=end)
            )
        filters['whitelists'] |= filter_whitelists

    # Rooms
    if '5' in aff and Room.can_view_all(user):
        filter_rooms = Q(
            details__icontains=word
        ) | Q(
            name__icontains=word
        ) | Q(
            port__details=word
        )
        filters['rooms'] |= filter_rooms

    # Switch ports
    if '6' in aff and User.can_view_all(user):
        filter_ports = Q(
            room__name__icontains=word
        ) | Q(
            machine_interface__domain__name__icontains=word
        ) | Q(
            related__switch__interface__domain__name__icontains=word
        ) | Q(
            radius__icontains=word
        ) | Q(
            vlan_force__name__icontains=word
        ) | Q(
            details__icontains=word
        )
        if is_int(word):
            filter_ports |= Q(
                port=word
            )
        filters['ports'] |= filter_ports

    # Switches
    if '7' in aff and Switch.can_view_all(user):
        filter_switches = Q(
            interface__domain__name__icontains=word
        ) | Q(
            interface__ipv4__ipv4__icontains=word
        ) | Q(
            switchbay__building__name__icontains=word
        ) | Q(
            stack__name__icontains=word
        ) | Q(
            model__reference__icontains=word
        ) | Q(
            model__constructor__name__icontains=word
        ) | Q(
            interface__details__icontains=word
        )
        if is_int(word):
            filter_switches |= Q(
                number=word
            ) | Q(
                stack_member_id=word
            )
        filters['switches'] |= filter_switches

    return filters


def get_words(query):
    """Function used to split the uery in different words to look for.
    The rules are simple :
        - anti-slash ('\\') is used to escape characters
        - anything between quotation marks ('"') is kept intact (not
            interpreted as separators) excepts anti-slashes used to escape
        - spaces (' ') and commas (',') are used to separated words
    """

    words = []
    i = 0
    keep_intact = False
    escaping_char = False
    for char in query:
        if i >= len(words):
            # We are starting a new word
            words.append('')
        if escaping_char:
            # The last char war a \ so we escape this char
            escaping_char = False
            words[i] += char
            continue
        if char == '\\':
            # We need to escape the next char
            escaping_char = True
            continue
        if char == '"':
            # Toogle the keep_intact state, if true, we are between two "
            keep_intact = not keep_intact
            continue
        if keep_intact:
            # If we are between two ", ignore separators
            words[i] += char
            continue
        if char == ' ' or char == ',':
            # If we encouter a separator outside of ", we create a new word
            if words[i] is not '':
                i += 1
            continue
        # If we haven't encountered any special case, add the char to the word
        words[i] += char

    return words


def get_results(query, request, params):
    """The main function of the search procedure. It gather the filters for
    each of the different words of the query and concatenate them into a
    single filter. Then it calls 'finish_results' and return the queryset of
    objects to display as results"""

    start = params.get('s', None)
    end = params.get('e', None)
    user_state = params.get('u', initial_choices(CHOICES_USER))
    aff = params.get('a', initial_choices(CHOICES_AFF))

    filters = {
        'users': Q(),
        'clubs': Q(),
        'machines': Q(),
        'factures': Q(),
        'bans': Q(),
        'whitelists': Q(),
        'rooms': Q(),
        'ports': Q(),
        'switches': Q()
    }

    words = get_words(query)
    for word in words:
        filters = search_single_word(
            word,
            filters,
            request.user,
            start,
            end,
            user_state,
            aff
        )

    results = {
        'users': Adherent.objects.filter(filters['users']),
        'clubs': Club.objects.filter(filters['clubs']),
        'machines': Machine.objects.filter(filters['machines']),
        'factures': Facture.objects.filter(filters['factures']),
        'bans': Ban.objects.filter(filters['bans']),
        'whitelists': Whitelist.objects.filter(filters['whitelists']),
        'rooms': Room.objects.filter(filters['rooms']),
        'ports': Port.objects.filter(filters['ports']),
        'switches': Switch.objects.filter(filters['switches'])
    }

    results = finish_results(
        results,
        request.GET.get('col'),
        request.GET.get('order')
    )
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
