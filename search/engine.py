# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2019  Jean-Romain Garnier
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
Augustin lemesle, Gabriel Détraz, Lara Kermarec, Maël Kervella,
Jean-Romain Garnier
Gplv2"""

from __future__ import unicode_literals

from netaddr import EUI, AddrFormatError

from django.db.models import Q
from users.models import User, Adherent, Club, Ban, Whitelist
from machines.models import Machine
from topologie.models import Port, Switch, Room
from cotisations.models import Facture
from preferences.models import GeneralOption
from re2o.base import SortTable, re2o_paginator


class Query:
    """Class representing a query.
    It can contain the user-entered text, the operator for the query,
    and a list of subqueries"""
    def __init__(self, text=""):
        self.text = text  # Content of the query
        self.operator = None  # Whether a special char (ex "+") was used
        self.subqueries = None   # When splitting the query in subparts

    def add_char(self, char):
        """Add the given char to the query's text"""
        self.text += char

    def add_operator(self, operator):
        """Consider a new operator was entered, and that it must be processed.
        The query's current text is moved to self.subqueries in the form
        of a plain Query object"""
        self.operator = operator

        if self.subqueries is None:
            self.subqueries = []

        self.subqueries.append(Query(self.text))
        self.text = ""

    @property
    def plaintext(self):
        """Returns a textual representation of the query's content"""
        if self.operator is not None:
            return self.operator.join([q.plaintext for q in self.subqueries])

        return self.text


def filter_fields():
    """Return the list of fields the search applies to"""
    return ["users",
            "clubs",
            "machines",
            "factures",
            "bans",
            "whitelists",
            "rooms",
            "ports",
            "switches"]


def empty_filters():
    """Build empty filters used by Django"""
    return {f: Q() for f in filter_fields()}


def is_int(variable):
    """ Check if the variable can be casted to an integer """
    try:
        int(variable)
    except ValueError:
        return False
    else:
        return True


def finish_results(request, results, col, order):
    """Sort the results by applying filters and then limit them to the
    number of max results. Finally add the info of the nmax number of results
    to the dict"""
    results["users"] = SortTable.sort(
        results["users"], col, order, SortTable.USERS_INDEX
    )
    results["clubs"] = SortTable.sort(
        results["clubs"], col, order, SortTable.USERS_INDEX
    )
    results["machines"] = SortTable.sort(
        results["machines"], col, order, SortTable.MACHINES_INDEX
    )
    results["factures"] = SortTable.sort(
        results["factures"], col, order, SortTable.COTISATIONS_INDEX
    )
    results["bans"] = SortTable.sort(
        results["bans"], col, order, SortTable.USERS_INDEX_BAN
    )
    results["whitelists"] = SortTable.sort(
        results["whitelists"], col, order, SortTable.USERS_INDEX_WHITE
    )
    results["rooms"] = SortTable.sort(
        results["rooms"], col, order, SortTable.TOPOLOGIE_INDEX_ROOM
    )
    results["ports"] = SortTable.sort(
        results["ports"], col, order, SortTable.TOPOLOGIE_INDEX_PORT
    )
    results["switches"] = SortTable.sort(
        results["switches"], col, order, SortTable.TOPOLOGIE_INDEX
    )

    max_result = GeneralOption.get_cached_value("search_display_page")
    for name, val in results.items():
        page_arg = name + "_page"
        results[name] = re2o_paginator(request, val.distinct(), max_result, page_arg=page_arg)

    results.update({"max_result": max_result})

    return results


def search_single_word(word, filters, user, start, end, user_state, aff):
    """ Construct the correct filters to match differents fields of some models
    with the given query according to the given filters.
    The match field are either CharField or IntegerField that will be displayed
    on the results page (else, one might not see why a result has matched the
    query). IntegerField are matched against the query only if it can be casted
    to an int."""

    # Users
    if "0" in aff:
        filter_clubs = (
            Q(surname__icontains=word)
            | Q(pseudo__icontains=word)
            | Q(room__name__icontains=word)
            | Q(email__icontains=word)
            | Q(telephone__icontains=word)
            | Q(room__name__icontains=word)
            | Q(room__building__name__icontains=word)
        )
        filter_users = (filter_clubs | Q(name__icontains=word))

        if not User.can_view_all(user)[0]:
            filter_clubs &= Q(id=user.id)
            filter_users &= Q(id=user.id)

        filter_clubs &= Q(state__in=user_state)
        filter_users &= Q(state__in=user_state)

        filters["users"] |= filter_users
        filters["clubs"] |= filter_clubs

    # Machines
    if "1" in aff:
        filter_machines = (
            Q(name__icontains=word)
            | (Q(user__pseudo__icontains=word) & Q(user__state__in=user_state))
            | Q(interface__domain__name__icontains=word)
            | Q(interface__domain__related_domain__name__icontains=word)
            | Q(interface__mac_address__icontains=word)
            | Q(interface__ipv4__ipv4__icontains=word)
        )
        try:
            _mac_addr = EUI(word, 48)
            filter_machines |= Q(interface__mac_address=word)
        except AddrFormatError:
            pass
        if not Machine.can_view_all(user)[0]:
            filter_machines &= Q(user__id=user.id)
        filters["machines"] |= filter_machines

    # Factures
    if "2" in aff:
        filter_factures = Q(user__pseudo__icontains=word) & Q(
            user__state__in=user_state
        )
        if start is not None:
            filter_factures &= Q(date__gte=start)
        if end is not None:
            filter_factures &= Q(date__lte=end)
        filters["factures"] |= filter_factures

    # Bans
    if "3" in aff:
        filter_bans = (
            Q(user__pseudo__icontains=word) & Q(user__state__in=user_state)
        ) | Q(raison__icontains=word)
        if start is not None:
            filter_bans &= (
                (Q(date_start__gte=start) & Q(date_end__gte=start))
                | (Q(date_start__lte=start) & Q(date_end__gte=start))
                | (Q(date_start__gte=start) & Q(date_end__lte=start))
            )
        if end is not None:
            filter_bans &= (
                (Q(date_start__lte=end) & Q(date_end__lte=end))
                | (Q(date_start__lte=end) & Q(date_end__gte=end))
                | (Q(date_start__gte=end) & Q(date_end__lte=end))
            )
        filters["bans"] |= filter_bans

    # Whitelists
    if "4" in aff:
        filter_whitelists = (
            Q(user__pseudo__icontains=word) & Q(user__state__in=user_state)
        ) | Q(raison__icontains=word)
        if start is not None:
            filter_whitelists &= (
                (Q(date_start__gte=start) & Q(date_end__gte=start))
                | (Q(date_start__lte=start) & Q(date_end__gte=start))
                | (Q(date_start__gte=start) & Q(date_end__lte=start))
            )
        if end is not None:
            filter_whitelists &= (
                (Q(date_start__lte=end) & Q(date_end__lte=end))
                | (Q(date_start__lte=end) & Q(date_end__gte=end))
                | (Q(date_start__gte=end) & Q(date_end__lte=end))
            )
        filters["whitelists"] |= filter_whitelists

    # Rooms
    if "5" in aff and Room.can_view_all(user):
        filter_rooms = (
            Q(details__icontains=word) | Q(name__icontains=word) | Q(port__details=word) | Q(building__name__icontains=word)
        )

        filters["rooms"] |= filter_rooms

    # Switch ports
    if "6" in aff and User.can_view_all(user):
        filter_ports = (
            Q(room__name__icontains=word)
            | Q(machine_interface__domain__name__icontains=word)
            | Q(related__switch__interface__domain__name__icontains=word)
            | Q(custom_profile__name__icontains=word)
            | Q(custom_profile__profil_default__icontains=word)
            | Q(details__icontains=word)
        )
        if is_int(word):
            filter_ports |= Q(port=word)
        filters["ports"] |= filter_ports

    # Switches
    if "7" in aff and Switch.can_view_all(user):
        filter_switches = (
            Q(interface__domain__name__icontains=word)
            | Q(interface__ipv4__ipv4__icontains=word)
            | Q(switchbay__building__name__icontains=word)
            | Q(stack__name__icontains=word)
            | Q(model__reference__icontains=word)
            | Q(model__constructor__name__icontains=word)
            | Q(interface__details__icontains=word)
        )
        if is_int(word):
            filter_switches |= Q(number=word) | Q(stack_member_id=word)
        filters["switches"] |= filter_switches

    return filters


def apply_filters(filters, user, aff):
    """ Apply the filters constructed by search_single_query.
    It also takes into account the visual filters defined during
    the search query.
    """
    # Results are later filled-in depending on the display filter
    results = {
        "users": Adherent.objects.none(),
        "clubs": Club.objects.none(),
        "machines": Machine.objects.none(),
        "factures": Facture.objects.none(),
        "bans": Ban.objects.none(),
        "whitelists": Whitelist.objects.none(),
        "rooms": Room.objects.none(),
        "ports": Port.objects.none(),
        "switches": Switch.objects.none(),
    }

    # Users and clubs
    if "0" in aff:
        results["users"] = Adherent.objects.filter(filters["users"])
        results["clubs"] = Club.objects.filter(filters["clubs"])

    # Machines
    if "1" in aff:
        results["machines"] = Machine.objects.filter(filters["machines"])

    # Factures
    if "2" in aff:
        results["factures"] = Facture.objects.filter(filters["factures"])

    # Bans
    if "3" in aff:
        results["bans"] = Ban.objects.filter(filters["bans"])

    # Whitelists
    if "4" in aff:
        results["whitelists"] = Whitelist.objects.filter(filters["whitelists"])

    # Rooms
    if "5" in aff and Room.can_view_all(user):
        results["rooms"] = Room.objects.filter(filters["rooms"])

    # Switch ports
    if "6" in aff and User.can_view_all(user):
        results["ports"] = Port.objects.filter(filters["ports"])

    # Switches
    if "7" in aff and Switch.can_view_all(user):
        results["switches"] = Switch.objects.filter(filters["switches"])

    return results


def search_single_query(query, filters, user, start, end, user_state, aff):
    """ Handle different queries an construct the correct filters using
    search_single_word"""
    if query.operator == "+":
        # Special queries with "+" operators should use & rather than |
        newfilters = empty_filters()
        for q in query.subqueries:
            # Construct an independent filter for each subquery
            subfilters = search_single_query(q, empty_filters(), user, start, end, user_state, aff)

            # Apply the subfilter
            for field in filter_fields():
                newfilters[field] &= subfilters[field]

        # Add these filters to the existing ones
        for field in filter_fields():
            filters[field] |= newfilters[field]

        return filters

    # Handle standard queries
    return search_single_word(query.text, filters, user, start, end, user_state, aff)


def create_queries(query):
    """Function used to split the query in different words to look for.
    The rules are the following :
        - anti-slash ('\\') is used to escape characters
        - anything between quotation marks ('"') is kept intact (not
            interpreted as separators) excepts anti-slashes used to escape
            Values in between quotation marks are not searched accross
            multiple field in the database (contrary to +)
        - spaces (' ') and commas (',') are used to separated words
        - "+" signs are used as "and" operators
    """
    # A dict representing the different queries extracted from the user's text
    queries = []
    current_query = None

    # Whether the query is between "
    keep_intact = False

    # Whether the previous char was a \
    escaping_char = False

    for char in query:
        if current_query is None:
            # We are starting a new word
            current_query = Query()

        if escaping_char:
            # The last char war a \ so we escape this char
            escaping_char = False
            current_query.add_char(char)
            continue

        if char == "\\":
            # We need to escape the next char
            escaping_char = True
            continue

        if char == '"':
            # Toogle the keep_intact state, if true, we are between two "
            keep_intact = not keep_intact
            continue

        if keep_intact:
            # If we are between two ", ignore separators
            current_query.add_char(char)
            continue

        if char == "+":
            if len(current_query.text) == 0:
                # Can't sart a query with a "+", consider it escaped
                current_query.add_char(char)
                continue

            current_query.add_operator("+")
            continue

        if char == " " or char == ",":
            # If we encouter a separator outside of ", we create a new word

            if len(current_query.text) == 0:
                # Discard empty queries
                continue

            if current_query.operator is not None:
                # If we were building a special structure, finish building it
                current_query.add_operator(current_query.operator)

            # Save the query and start a new one
            queries.append(current_query)
            current_query = None
            continue

        # If we haven't encountered any special case, add the char to the word
        current_query.add_char(char)

    # Save the current working query if necessary
    if current_query is not None:
        if current_query.operator is not None:
            # There was an operator supposed to split multiple words
            if len(current_query.text) > 0:
                # Finish the current search
                current_query.add_operator(current_query.operator)

        queries.append(current_query)

    return queries
