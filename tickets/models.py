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

from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template import loader
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property

from reversion.models import Version

from re2o.mixins import AclMixin
from re2o.mail_utils import send_mail_object
from django.core.mail import EmailMessage

from preferences.models import GeneralOption

import users.models

from .preferences.models import TicketOption


class Ticket(AclMixin, models.Model):
    """Model of a ticket.

    Attributes:
        user: User, the user creating the ticket.
        title: the title of the ticket, chosen by the user.
        description: the main content of the ticket, written by the user to
            explain their problem.
        date: datetime, the date of creation of the ticket.
        email: the email address used to reply to the ticket.
        solved: boolean, True if the problem explained in the ticket has been
            solved, False otherwise. It is used to see easily which tickets
            still require attention.
        language: the language of the ticket, used to select the appropriate
            template when sending automatic emails, e.g. ticket creation.
        request: the request displayed if there is an error when sending emails
            related to the ticket.
    """

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
    language = models.CharField(
        max_length=16, help_text=_("Language of the ticket."), default="en" 
    )
    request = None

    class Meta:
        permissions = (("view_ticket", _("Can view a ticket object")),)
        verbose_name = _("ticket")
        verbose_name_plural = _("tickets")

    def __str__(self):
        if self.user:
            return _("Ticket from {name}. Date: {date}.").format(name=self.user.get_full_name(),date=self.date)
        else:
            return _("Anonymous ticket. Date: %s.") % (self.date)

    @cached_property
    def opened_by(self):
        """Get the full name of the user who opened the ticket."""
        if self.user:
            return self.user.get_full_name()
        else:
            return _("Anonymous user") 

    @cached_property
    def get_mail(self):
        """Get the email address of the user who opened the ticket."""
        return self.email or self.user.get_mail 

    def publish_mail(self):
        """Send an email for a newly opened ticket to the address set in the
        preferences.
        """
        site_url = GeneralOption.get_cached_value("main_site_url")
        to_addr = TicketOption.get_cached_value("publish_address")
        context = {"ticket": self, "site_url": site_url}

        if self.language == "fr":
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
            reply_to=[self.get_mail],
        )
        send_mail_object(mail_to_send, self.request)


    def can_view(self, user_request, *_args, **_kwargs):
        """Check that the user has the right to view the ticket
        or that it is the author."""
        if (
            not user_request.has_perm("tickets.view_ticket")
            and self.user != user_request
        ):
            return (
                False,
                _("You don't have the right to view other tickets than yours."),
                ("tickets.view_ticket",),
            )
        else:
            return True, None, None

    @staticmethod
    def can_view_all(user_request, *_args, **_kwargs):
        """Check that the user has access to the list of all tickets."""
        can = user_request.has_perm("tickets.view_ticket")
        return (
            can,
            _("You don't have the right to view the list of tickets.")
            if not can
            else None,
            ("tickets.view_ticket",),
        )

    def can_create(user_request, *_args, **_kwargs):
        """Authorise all users to open tickets."""
        return True, None, None


class CommentTicket(AclMixin, models.Model):
    """A comment of a ticket.

    Attributes:
        date: datetime, the date of creation of the comment.
        comment: the text written as a comment to a ticket.
        parent_ticket: the ticket which is commented.
        created_at: datetime, the date of creation of the comment.
        created_by: the user who wrote the comment.
        request: the request used if there is an error when sending emails
            related to the comment.
    """

    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(
        max_length=4095,
        blank=False,
        null=False,
    )
    parent_ticket = models.ForeignKey(
        "Ticket", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="ticket_comment",
    )
    request = None

    class Meta:
        permissions = (("view_commentticket", _("Can view a ticket object")),)
        verbose_name = _("ticket")
        verbose_name_plural = _("tickets")

    @cached_property
    def comment_id(self):
        return CommentTicket.objects.filter(parent_ticket=self.parent_ticket, pk__lt=self.pk).count() + 1

    def can_view(self, user_request, *_args, **_kwargs):
        """Check that the user has the right to view the ticket comment
        or that it is the author."""
        if (
            not user_request.has_perm("tickets.view_commentticket")
            and self.parent_ticket.user != user_request
        ):
            return (
                False,
                _("You don't have the right to view other tickets comments than yours."),
                ("tickets.view_commentticket",),
            )
        else:
            return True, None, None

    def can_edit(self, user_request, *_args, **_kwargs):
        """Check that the user has the right to edit the ticket comment
        or that it is the author."""
        if (
            not user_request.has_perm("tickets.change_commentticket")
            and (self.parent_ticket.user != user_request or self.parent_ticket.user != self.created_by)
        ):
            return (
                False,
                _("You don't have the right to edit other tickets comments than yours."),
                ("tickets.change_commentticket",),
            )
        else:
            return True, None, None

    @staticmethod
    def can_view_all(user_request, *_args, **_kwargs):
        """Check that the user has access to the list of all tickets comments."""
        can = user_request.has_perm("tickets.view_commentticket")
        return (
            can,
            _("You don't have the right to view the list of tickets.")
            if not can
            else None,
            ("tickets.view_commentticket",),
        )

    def __str__(self):
        return "Comment " + str(self.comment_id) + " on " + str(self.parent_ticket)

    def publish_mail(self):
        """Send an email for a newly written comment to the ticket's author and
        to the address set in the preferences.
        """
        site_url = GeneralOption.get_cached_value("main_site_url")
        to_addr = TicketOption.get_cached_value("publish_address")
        context = {"comment": self, "site_url": site_url}

        if self.parent_ticket.language == "fr":
            template = loader.get_template("tickets/update_mail_fr")
        else:
            template = loader.get_template("tickets/update_mail_en")
        obj = _("Update of your ticket")
        mail_to_send = EmailMessage(
            obj,
            template.render(context),
            GeneralOption.get_cached_value("email_from"),
            [to_addr, self.parent_ticket.get_mail],
            reply_to=[to_addr, self.parent_ticket.get_mail],
        )
        send_mail_object(mail_to_send, self.request)


@receiver(post_save, sender=Ticket)
def ticket_post_save(**kwargs):
    """Call the method to publish an email when a ticket is created."""
    if kwargs["created"]:
        if TicketOption.get_cached_value("publish_address"):
            ticket = kwargs["instance"]
            ticket.publish_mail()


@receiver(post_save, sender=CommentTicket)
def comment_post_save(**kwargs):
    """Call the method to publish an email when a comment is created."""
    if kwargs["created"]:
        if TicketOption.get_cached_value("publish_address"):
            comment = kwargs["instance"]
            comment.publish_mail()
