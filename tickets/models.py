from django.db import models
from django.utils.translation import ugettext_lazy as _

import users.models

class Ticket(models.Model):
    """Class définissant un ticket"""

    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE,
        related_name="tickets")
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
