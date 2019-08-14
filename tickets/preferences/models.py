from django.db import models
from django.utils.translation import ugettext_lazy as _

class Preferences(models.Model):
    """ Definition of the ticket's settings"""

    publish_address = models.EmailField(
        help_text = _("Email address to publish the new tickets (leave empty for no publications)"),
        max_length = 1000,
        null = True)
    class Meta:
        verbose_name = _("Ticket's settings")
