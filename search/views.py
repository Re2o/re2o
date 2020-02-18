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
Augustin lemesle, Gabriel Détraz, Lara Kermarec, Maël Kervella
Gplv2"""


from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from users.models import User
from cotisations.models import Cotisation
from machines.models import Machine
from search.forms import (
    SearchForm,
    SearchFormPlus,
    CHOICES_USER,
    CHOICES_AFF,
    initial_choices,
)
from re2o.acl import can_view_all

from engine import *


def get_results(query, request, params):
    """The main function of the search procedure. It gather the filters for
    each of the different words of the query and concatenate them into a
    single filter. Then it calls 'finish_results' and return the queryset of
    objects to display as results"""

    start = params.get("s", None)
    end = params.get("e", None)
    user_state = params.get("u", initial_choices(CHOICES_USER))
    aff = params.get("a", initial_choices(CHOICES_AFF))

    filters = empty_filters()

    queries = create_queries(query)
    for q in queries:
        filters = search_single_query(
            q, filters, request.user, start, end, user_state, aff
        )

    results = apply_filters(filters, request.user, aff)
    results = finish_results(request, results, request.GET.get("col"), request.GET.get("order"))
    results.update({"search_term": query})

    return results


@login_required
@can_view_all(User, Machine, Cotisation)
def search(request):
    """ La page de recherche standard """
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid():
        return render(
            request,
            "search/index.html",
            get_results(
                search_form.cleaned_data.get("q", ""), request, search_form.cleaned_data
            ),
        )
    return render(request, "search/search.html", {"search_form": search_form})


@login_required
@can_view_all(User, Machine, Cotisation)
def searchp(request):
    """ La page de recherche avancée """
    search_form = SearchFormPlus(request.GET or None)
    if search_form.is_valid():
        return render(
            request,
            "search/index.html",
            get_results(
                search_form.cleaned_data.get("q", ""), request, search_form.cleaned_data
            ),
        )
    return render(request, "search/search.html", {"search_form": search_form})
