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
"""
Ticket model
"""


from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template import loader
from django.db.models.signals import post_save
from django.dispatch import receiver

from re2o.mixins import AclMixin
from django.core.mail import EmailMessage

from preferences.models import GeneralOption

import users.models

from .preferences.models import TicketOption


class Ticket(AclMixin, models.Model):
    """Model of a ticket"""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="tickets",
        blank=True,
        null=True,
    )
    title = models.CharField(
        max_length=255, help_text=_("Title of the ticket."), blank=False, null=False
    )
    description = models.TextField(
        max_length=3000,
        blank=False,
        null=False,
    )
    date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(
        help_text=_("An email address to get back to you."), max_length=100, null=True
    )
    solved = models.BooleanField(default=False)
    request = None

    class Meta:
        permissions = (("view_tickets", _("Can view a ticket object")),)
        verbose_name = _("ticket")
        verbose_name_plural = _("tickets")

    def __str__(self):
        if self.user:
            return _("Ticket from %(name)s. Date: %(date)s.").format(name=self.user.surname, date=self.date)
        else:
            return _("Anonymous ticket. Date: %s.") % (self.date)

    def publish_mail(self):
        site_url = GeneralOption.get_cached_value("main_site_url")
        to_addr = TicketOption.get_cached_value("publish_address")
        context = {"ticket": self, "site_url": site_url}

        language = getattr(self.request, "LANGUAGE_CODE", "en")
        if language == "fr":
            obj = "Nouveau ticket ouvert"
            template = loader.get_template("tickets/publication_mail_fr")
        else:
            obj = "New ticket opened"
            template = loader.get_template("tickets/publication_mail_en")

        mail_to_send = EmailMessage(
            obj,
            template.render(context),
            GeneralOption.get_cached_value("email_from"),
            [to_addr],
            reply_to=[self.email],
        )
        mail_to_send.send(fail_silently=False)


    def can_view(self, user_request, *_args, **_kwargs):
        """ Check that the user has the right to view the ticket
        or that it is the author"""
        if (
            not user_request.has_perm("tickets.view_tickets")
            and self.user != user_request
        ):
            return (
                False,
                _("You don't have the right to view other tickets than yours."),
                ("tickets.view_tickets",),
            )
        else:
            return True, None, None

    @staticmethod
    def can_view_all(user_request, *_args, **_kwargs):
        """ Check that the user has access to the list of all tickets"""
        can = user_request.has_perm("tickets.view_tickets")
        return (
            can,
            _("You don't have the right to view the list of tickets.")
            if not can
            else None,
            ("tickets.view_tickets",),
        )

    def can_create(user_request, *_args, **_kwargs):
        """ Authorise all users to open tickets """
        return True, None, None


@receiver(post_save, sender=Ticket)
def ticket_post_save(**kwargs):
    """ Send the mail to publish the new ticket """
    if kwargs["created"]:
        if TicketOption.get_cached_value("publish_address"):
            ticket = kwargs["instance"]
            ticket.publish_mail()
