from django.db import models
from django.utils.translation import ugettext_lazy as _

class Preferences(models.Model):
    """ Definition of the ticket's settings"""

    publish_address = models.EmailField(
        help_text = _("Email address to publish the new tickets (leave empty for no publications)"),
        max_length = 1000,
        null = True)
    LANG_FR = 0
    LANG_EN = 1
    LANGUES = (
        (0,_("Français")),
        (1,_("English")),
    )
    mail_language = models.IntegerField(choices=LANGUES,default = LANG_FR)
    class Meta:
        verbose_name = _("Ticket's settings")
