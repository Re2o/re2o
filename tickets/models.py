from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.template import Context, loader
from django.db.models.signals import post_save
from django.dispatch import receiver

from re2o.mixins import AclMixin

from preferences.models import GeneralOption

import users.models

class Ticket(AclMixin, models.Model):
    """Class définissant un ticket"""

    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE,
        related_name="tickets",
        blank=True,
        null=True)
    title = models.CharField(
        max_length=255,
        help_text=_("Nom du ticket"),
        blank=False,
        null=False,)
    description = models.TextField(
        max_length=3000,
        help_text=_("Description du ticket"),
        blank=False,
        null=False)
    date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(
        help_text = _("Une adresse mail pour vous recontacter"),
        max_length=100, 
        null=True)
    assigned_staff = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name="tickets_assigned",
        blank=True,
        null=True)
    #categories = models.OneToManyFiled('Category')
    solved = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")

    def __str__(self):
        return "Ticket de {} date: {}".format(self.user.surname,self.date)

    def publish_mail(self):
        to_addr = Preferences.objects.first().publish_address
        template = loader.get_template('tickets/publication_mail')
        context = Context({'ticket':self})
        send_mail(
            'Nouvelle ouverture de ticket',
            template.render(context),
            GeneralOption.get_cached_value('email_from'),
            [to_addr],
            fail_silently = False)
    
    def can_view(self, user_request, *_args, **_kwargs):
        """Verifie que la personne à le droit pour voir le ticket
        ou qu'elle est l'auteur du ticket"""
        if (not user_request.has_perm('tickets.view_ticket') and self.user != user_request):
            return False, _("You don't have the right to view other Tickets than yours.")
        else:
            return True, None
    
    @staticmethod
    def can_view_all(user_request, *_args, **_kwargs):
        """Vérifie si l'user a acccés à la liste de tous les tickets"""
        return(
            user_request.has_perm('tickets.view_tickets'),
            _("You don't have the right to view the list of tickets.")
        )

    def can_create(user_request,*_args, **_kwargs):
        """Autorise tout les utilisateurs à créer des tickets"""
        return True,None
"""
class Preferences(models.Model):
    
    publish_address = models.EmailField(
        help_text = _("Adresse mail pour annoncer les nouveau tickets (laisser vide pour ne rien annoncer)"),
        max_length = 1000,
        null = True)
    class Meta:
        verbose_name = _("Préférences des tickets")
"""

@receiver(post_save, sender=Ticket)
def ticket_post_save(**kwargs):
    """Envoit du mail de publication du ticket"""
    if kwargs['created']:
        if Preferences.objects.first().publish_address:
            ticket = kwargs['instance']
            ticket.publish_mail()
