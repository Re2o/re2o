from django.db import models
from django.utils.translation import ugettext_lazy as _

class Preferences(models.Model):
    """ Class cannonique définissants les préférences des tickets """

    publish_address = models.EmailField(
        help_text = _("Adresse mail pour annoncer les nouveau tickets (laisser vide pour ne rien annoncer)"),
        max_length = 1000,
        null = True)
    class Meta:
        verbose_name = _("Préférences des tickets")
