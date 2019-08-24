# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
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


from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from re2o.mixins import AclMixin

from preferences.models import PreferencesModel

class PreferencesUser(AclMixin, PreferencesModel):
    """Options pour l'user : obligation ou nom du telephone,
    activation ou non du solde, autorisation du negatif, fingerprint etc"""

    is_tel_mandatory = models.BooleanField(default=True)
    gpg_fingerprint = models.BooleanField(default=True)
    all_can_create_club = models.BooleanField(
        default=False,
        help_text=_("Users can create a club.")
    )
    all_can_create_adherent = models.BooleanField(
        default=False,
        help_text=_("Users can create a member."),
    )

    shell_default = models.OneToOneField(
        'users.ListShell',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    self_change_shell = models.BooleanField(
        default=False,
        help_text=_("Users can edit their shell.")
    )   
    self_change_room = models.BooleanField(
        default=False,
        help_text=_("Users can edit their room.")
    )
    local_email_accounts_enabled = models.BooleanField(
        default=False,
        help_text=_("Enable local email accounts for users.")
    )
    local_email_domain = models.CharField(
        max_length=32,
        default="@example.org",
        help_text=_("Domain to use for local email accounts")
    )
    max_email_address = models.IntegerField(
        default=15,
        help_text=_("Maximum number of local email addresses for a standard"
                    " user.")
    )
    delete_notyetactive = models.IntegerField(
        default=15,
        help_text=_("Not yet active users will be deleted after this number of"
                    " days.")
    )
    self_adhesion = models.BooleanField(
        default=False,
        help_text=_("A new user can create their account on Re2o.")
    )
    all_users_active = models.BooleanField(
        default=False,
        help_text=_("If True, all new created and connected users are active."
                    " If False, only when a valid registration has been paid.")
    )

    class Meta:
        permissions = (
            ("view_optionaluser", _("Can view the user options")),
        )
        verbose_name = _("user options")

    def clean(self):
        """Clean model:
        Check the mail_extension
        """
        if self.local_email_domain[0] != "@":
            raise ValidationError(_("Email domain must begin with @"))


@receiver(post_save, sender=PreferencesUser)
def preferencesUser_post_save(**kwargs):
    """Ecriture dans le cache"""
    user_pref = kwargs['instance']
    user_pref.set_in_cache()
