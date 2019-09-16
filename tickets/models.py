from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.template import loader
from django.db.models.signals import post_save
from django.dispatch import receiver

from re2o.mixins import AclMixin

from preferences.models import GeneralOption

import users.models

from .preferences.models import Preferences

class Ticket(AclMixin, models.Model):
    """Model of a ticket"""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="tickets",
        blank=True,
        null=True)
    title = models.CharField(
        max_length=255,
        help_text=_("Title of the ticket"),
        blank=False,
        null=False,)
    description = models.TextField(
        max_length=3000,
        help_text=_("Description of the ticket"),
        blank=False,
        null=False)
    date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(
        help_text = _("An email address to get back to you"),
        max_length=100,
        null=True)
    solved = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("view_tickets", _("Can view a ticket object")),
        )
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")

    def __str__(self):
        if self.user:
            return "Ticket from {}. Date: {}".format(self.user.surname,self.date)
        else:
            return "Anonymous Ticket. Date: {}".format(self.date)

    def publish_mail(self):
        site_url = GeneralOption.objects.first().main_site_url
        to_addr = Preferences.objects.first().publish_address
        context = {'ticket':self,'site_url':site_url}

        lang = Preferences.objects.first().mail_language
        if(lang == 0):
            obj = 'Nouvelle ouverture de ticket'
            template = loader.get_template('tickets/publication_mail_fr')
        else:
            obj = 'New ticket opened'
            template = loader.get_template('tickets/publication_mail_en')
        send_mail(
            obj,
            template.render(context),
            GeneralOption.get_cached_value('email_from'),
            [to_addr],
            fail_silently = False)

    def can_view(self, user_request, *_args, **_kwargs):
        """ Check that the user has the right to view the ticket
        or that it is the author"""
        if (not user_request.has_perm('tickets.view_ticket') and self.user != user_request):
            return (
                False,
                _("You don't have the right to view other tickets than yours."),
                ('tickets.view_ticket',)
            )
        else:
            return True, None, None

    @staticmethod
    def can_view_all(user_request, *_args, **_kwargs):
        """ Check that the user has access to the list of all tickets"""
        return(
            user_request.has_perm('tickets.view_tickets'),
            _("You don't have the right to view the list of tickets."),
            ('tickets.view_tickets',)
        )

    def can_create(user_request,*_args, **_kwargs):
        """ Authorise all users to open tickets """
        return True, None, None

@receiver(post_save, sender=Ticket)
def ticket_post_save(**kwargs):
    """ Send the mail to publish the new ticket """
    if kwargs['created']:
        if Preferences.objects.first().publish_address:
            ticket = kwargs['instance']
            ticket.publish_mail()
