# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
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
# Lara Kermarec, Gabriel Détraz, Lemesle Augustin
# Gplv2

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.forms import modelformset_factory
from re2o.views import form

from re2o.base import re2o_paginator

from re2o.acl import can_view, can_view_all, can_edit, can_create

from preferences.models import GeneralOption

from .models import Ticket

from .preferences.models import Preferences

from .forms import NewTicketForm, ChangeStatusTicketForm

from .preferences.forms import EditPreferencesForm


def new_ticket(request):
    """ Ticket creation view"""
    ticketform = NewTicketForm(request.POST or None)

    if request.method == "POST":
        ticketform = NewTicketForm(request.POST)

        if ticketform.is_valid():
            email = ticketform.cleaned_data.get("email")
            ticket = ticketform.save(commit=False)
            ticket.request = request

            if request.user.is_authenticated:
                ticket.user = request.user
                ticket.save()
                messages.success(
                    request,
                    _(
                        "Your ticket has been succesfully opened. We will take care of it as soon as possible."
                    ),
                )
                return redirect(
                    reverse("users:profil", kwargs={"userid": str(request.user.id)})
                )
            if not request.user.is_authenticated and email != "":
                ticket.save()
                messages.success(
                    request,
                    _(
                        "Your ticket has been succesfully opened. We will take care of it as soon as possible."
                    ),
                )
                return redirect(reverse("index"))
            else:
                messages.error(
                    request,
                    _(
                        "You are not authenticated. Please log in or provide an email address so we can get back to you."
                    ),
                )
                return form(
                    {"ticketform": ticketform}, "tickets/form_ticket.html", request
                )

    else:
        ticketform = NewTicketForm
    return form({"ticketform": ticketform}, "tickets/form_ticket.html", request)


@login_required
@can_view(Ticket)
def aff_ticket(request, ticket, ticketid):
    """View to display only one ticket"""
    changestatusform = ChangeStatusTicketForm(request.POST)
    if request.method == "POST":
        ticket.solved = not ticket.solved
        ticket.save()
    return render(
        request,
        "tickets/aff_ticket.html",
        {"ticket": ticket, "changestatusform": changestatusform},
    )


@login_required
@can_view_all(Ticket)
def aff_tickets(request):
    """ View to display all the tickets """
    tickets_list = Ticket.objects.all().order_by("-date")
    nbr_tickets = tickets_list.count()
    nbr_tickets_unsolved = tickets_list.filter(solved=False).count()
    if nbr_tickets:
        last_ticket_date = tickets_list.first().date
    else:
        last_ticket_date = _("Never")

    pagination_number = GeneralOption.get_cached_value("pagination_number")

    tickets = re2o_paginator(request, tickets_list, pagination_number)

    context = {
        "tickets_list": tickets,
        "last_ticket_date": last_ticket_date,
        "nbr_tickets": nbr_tickets,
        "nbr_tickets_unsolved": nbr_tickets_unsolved,
    }

    return render(request, "tickets/index.html", context=context)


def edit_preferences(request):
    """ View to edit the settings of the tickets """

    preferences_instance, created = Preferences.objects.get_or_create(id=1)
    preferencesform = EditPreferencesForm(
        request.POST or None, instance=preferences_instance
    )

    if preferencesform.is_valid():
        if preferencesform.changed_data:
            preferencesform.save()
            messages.success(request, _("The tickets preferences were edited."))
            return redirect(reverse("preferences:display-options"))
        else:
            messages.error(request, _("Invalid form."))
            return form(
                {"preferencesform": preferencesform},
                "tickets/form_preferences.html",
                request,
            )
    return form(
        {"preferencesform": preferencesform}, "tickets/form_preferences.html", request
    )


# views cannoniques des apps optionnels
def profil(request, user):
    """ View to display the ticket's module on the profil"""
    tickets_list = Ticket.objects.filter(user=user).all().order_by("-date")
    nbr_tickets = tickets_list.count()
    nbr_tickets_unsolved = tickets_list.filter(solved=False).count()
    if nbr_tickets:
        last_ticket_date = tickets_list.first().date
    else:
        last_ticket_date = _("Never")

    pagination_number = GeneralOption.get_cached_value("pagination_large_number")

    tickets = re2o_paginator(request, tickets_list, pagination_number)

    context = {
        "tickets_list": tickets,
        "last_ticket_date": last_ticket_date,
        "nbr_tickets": nbr_tickets,
        "nbr_tickets_unsolved": nbr_tickets_unsolved,
    }
    return render_to_string(
        "tickets/profil.html", context=context, request=request, using=None
    )


def preferences(request):
    """ View to display the settings of the tickets in the preferences page"""
    pref, created = Preferences.objects.get_or_create(id=1)
    context = {
        "preferences": pref,
        "language": str(pref.LANGUES[pref.mail_language][1]),
    }
    return render_to_string(
        "tickets/preferences.html", context=context, request=request, using=None
    )


def contact(request):
    """View to display a contact address on the contact page
    used here to display a link to open a ticket"""
    return render_to_string("tickets/contact.html")


def navbar_user():
    """View to display the ticket link in thet user's dropdown in the navbar"""
    return ("users", render_to_string("tickets/navbar.html"))


def navbar_logout():
    """View to display the ticket link to log out users"""
    return render_to_string("tickets/navbar_logout.html")
