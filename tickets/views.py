# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Arthur Grisel-Davy
# Copyright © 2020  Gabriel Détraz
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

from re2o.acl import (
    can_view,
    can_view_all, 
    can_edit, 
    can_create, 
    can_delete
)

from preferences.models import GeneralOption

from .models import Ticket, CommentTicket

from .forms import NewTicketForm, EditTicketForm, CommentTicketForm


def new_ticket(request):
    """View used to display the creation form of tickets."""
    ticketform = NewTicketForm(request.POST or None, request=request)
    if ticketform.is_valid():
        ticketform.save()
        messages.success(
            request,
            _(
                "Your ticket has been succesfully opened. We will take care of it as soon as possible."
            ),
        )
        if not request.user.is_authenticated:
            return redirect(reverse("index"))
        else:
            return redirect(
                 reverse("users:profil", kwargs={"userid": str(request.user.id)})
            )
    return form(
        {"ticketform": ticketform, 'action_name': ("Create a ticket")}, "tickets/edit.html", request
    )


@login_required
@can_view(Ticket)
def aff_ticket(request, ticket, ticketid):
    """View used to display a single ticket."""
    comments = CommentTicket.objects.filter(parent_ticket=ticket)
    return render(
        request,
        "tickets/aff_ticket.html",
        {"ticket": ticket, "comments": comments},
    )


@login_required
@can_edit(Ticket)
def change_ticket_status(request, ticket, ticketid):
    """View used to change a ticket's status."""
    ticket.solved = not ticket.solved
    ticket.save()
    return redirect(
        reverse("tickets:aff-ticket", kwargs={"ticketid": str(ticketid)})
    )


@login_required
@can_edit(Ticket)
def edit_ticket(request, ticket, ticketid):
    """View used to display the edit form of tickets."""
    ticketform = EditTicketForm(request.POST or None, instance=ticket)
    if ticketform.is_valid():
        ticketform.save()
        messages.success(
            request,
            _(
                "Ticket has been updated successfully"
            ),
        )
        return redirect(
            reverse("tickets:aff-ticket", kwargs={"ticketid": str(ticketid)})
        )
    return form(
        {"ticketform": ticketform, 'action_name': ("Edit this ticket")}, "tickets/edit.html", request
    )


@login_required
@can_view(Ticket)
def add_comment(request, ticket, ticketid):
    """View used to add a comment to a ticket."""
    commentticket = CommentTicketForm(request.POST or None, request=request)
    if commentticket.is_valid():
        commentticket = commentticket.save(commit=False)
        commentticket.parent_ticket = ticket
        commentticket.created_by = request.user
        commentticket.save()
        messages.success(request, _("This comment was added."))
        return redirect(
            reverse("tickets:aff-ticket", kwargs={"ticketid": str(ticketid)})
        )
    return form(
        {"ticketform": commentticket, "action_name": _("Add a comment")}, "tickets/edit.html", request
    )


@login_required
@can_edit(CommentTicket)
def edit_comment(request, commentticket_instance, **_kwargs):
    """View used to edit a comment of a ticket."""
    commentticket = CommentTicketForm(request.POST or None, instance=commentticket_instance)
    if commentticket.is_valid():
        ticketid = commentticket_instance.parent_ticket.id
        if commentticket.changed_data:
            commentticket.save()
            messages.success(request, _("This comment was edited."))
        return redirect(
            reverse("tickets:aff-ticket", kwargs={"ticketid": str(ticketid)})
        )
    return form(
        {"ticketform": commentticket, "action_name": _("Edit")}, "tickets/edit.html", request,
    )


@login_required
@can_delete(CommentTicket)
def del_comment(request, commentticket, **_kwargs):
    """View used to delete a comment of a ticket."""
    if request.method == "POST":
        ticketid = commentticket.parent_ticket.id
        commentticket.delete()
        messages.success(request, _("The comment was deleted."))
        return redirect(
            reverse("tickets:aff-ticket", kwargs={"ticketid": str(ticketid)})
        )
    return form(
        {"objet": commentticket, "objet_name": _("Ticket Comment")}, "tickets/delete.html", request
    )


@login_required
@can_view_all(Ticket)
def aff_tickets(request):
    """View used to display all tickets."""
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


# Canonic views for optional apps
def aff_profil(request, user):
    """View used to display the tickets on a user's profile."""
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
        "tickets/aff_profil.html", context=context, request=request, using=None
    )


def contact(request):
    """View used to display contact addresses to be used for tickets on the
    contact page.
    """
    return render_to_string("tickets/contact.html")


def navbar_user():
    """View used to display a link to tickets in the navbar (in the dropdown
    menu Users).
    """
    return ("users", render_to_string("tickets/navbar.html"))


def navbar_logout():
    """View used to display a link to open tickets for logged out users."""
    return render_to_string("tickets/navbar_logout.html")
