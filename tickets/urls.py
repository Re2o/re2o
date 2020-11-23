# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
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
"""
Tickets url
"""

from django.conf.urls import url

from . import views
from .preferences.views import edit_options

urlpatterns = [
    url(r"^$", views.aff_tickets, name="aff-tickets"),
    url(r"^(?P<ticketid>[0-9]+)$", views.aff_ticket, name="aff-ticket"),
    url(r"^change_ticket_status/(?P<ticketid>[0-9]+)$", views.change_ticket_status, name="change-ticket-status"),
    url(r"^edit_ticket/(?P<ticketid>[0-9]+)$", views.edit_ticket, name="edit-ticket"),
    url(
        r"^edit_options/(?P<section>TicketOption)$",
        edit_options,
        name="edit-options",
    ),
    url(r"^new_ticket/$", views.new_ticket, name="new-ticket"),
    url(r"^add_comment/(?P<ticketid>[0-9]+)$", views.add_comment, name="add-comment"),
    url(r"^edit_comment/(?P<commentticketid>[0-9]+)$", views.edit_comment, name="edit-comment"),
    url(r"^del_comment/(?P<commentticketid>[0-9]+)$", views.del_comment, name="del-comment"),
]
