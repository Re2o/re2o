# -*- mode: python; coding: utf-8 -*-
# Re2o un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
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
"""
Reglages généraux, machines, utilisateurs, mail, general pour l'application.
"""
from __future__ import unicode_literals

from django.utils.functional import cached_property
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

import machines.models
from re2o.mixins import AclMixin


class PreferencesModel(models.Model):
    """ Base object for the Preferences objects
    Defines methods to handle the cache of the settings (they should
    not change a lot) """
    @classmethod
    def set_in_cache(cls):
        """ Save the preferences in a server-side cache """
        instance, _created = cls.objects.get_or_create()
        cache.set(cls().__class__.__name__.lower(), instance, None)
        return instance

    @classmethod
    def get_cached_value(cls, key):
        """ Get the preferences from the server-side cache """
        instance = cache.get(cls().__class__.__name__.lower())
        if instance is None:
            instance = cls.set_in_cache()
        return getattr(instance, key)

    class Meta:
        abstract = True


class OptionalUser(AclMixin, PreferencesModel):
    """Options pour l'user : obligation ou nom du telephone,
    activation ou non du solde, autorisation du negatif, fingerprint etc"""

    is_tel_mandatory = models.BooleanField(default=True)
    gpg_fingerprint = models.BooleanField(default=True)
    all_can_create_club = models.BooleanField(
        default=False,
        help_text=_("Users can create a club")
    )
    all_can_create_adherent = models.BooleanField(
        default=False,
        help_text=_("Users can create a member"),
    )
    self_adhesion = models.BooleanField(
        default=False,
        help_text=_("A new user can create their account on Re2o")
    )
    shell_default = models.OneToOneField(
        'users.ListShell',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    self_change_shell = models.BooleanField(
        default=False,
        help_text=_("Users can edit their shell")
    )
    local_email_accounts_enabled = models.BooleanField(
        default=False,
        help_text=_("Enable local email accounts for users")
    )
    local_email_domain = models.CharField(
        max_length=32,
        default="@example.org",
        help_text=_("Domain to use for local email accounts")
    )
    max_email_address = models.IntegerField(
        default=15,
        help_text=_("Maximum number of local email addresses for a standard"
                    " user")
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


@receiver(post_save, sender=OptionalUser)
def optionaluser_post_save(**kwargs):
    """Ecriture dans le cache"""
    user_pref = kwargs['instance']
    user_pref.set_in_cache()


class OptionalMachine(AclMixin, PreferencesModel):
    """Options pour les machines : maximum de machines ou d'alias par user
    sans droit, activation de l'ipv6"""

    SLAAC = 'SLAAC'
    DHCPV6 = 'DHCPV6'
    DISABLED = 'DISABLED'
    CHOICE_IPV6 = (
        (SLAAC, _("Autoconfiguration by RA")),
        (DHCPV6, _("IP addresses assigning by DHCPv6")),
        (DISABLED, _("Disabled")),
    )

    password_machine = models.BooleanField(default=False)
    max_lambdauser_interfaces = models.IntegerField(default=10)
    max_lambdauser_aliases = models.IntegerField(default=10)
    ipv6_mode = models.CharField(
        max_length=32,
        choices=CHOICE_IPV6,
        default='DISABLED'
    )
    create_machine = models.BooleanField(
        default=True
    )

    @cached_property
    def ipv6(self):
        """ Check if the IPv6 option is activated """
        return not self.get_cached_value('ipv6_mode') == 'DISABLED'

    class Meta:
        permissions = (
            ("view_optionalmachine", _("Can view the machine options")),
        )
        verbose_name = _("machine options")


@receiver(post_save, sender=OptionalMachine)
def optionalmachine_post_save(**kwargs):
    """Synchronisation ipv6 et ecriture dans le cache"""
    machine_pref = kwargs['instance']
    machine_pref.set_in_cache()
    if machine_pref.ipv6_mode != "DISABLED":
        for interface in machines.models.Interface.objects.all():
            interface.sync_ipv6()


class OptionalTopologie(AclMixin, PreferencesModel):
    """Reglages pour la topologie : mode d'accès radius, vlan où placer
    les machines en accept ou reject"""
    MACHINE = 'MACHINE'
    DEFINED = 'DEFINED'
    CHOICE_RADIUS = (
        (MACHINE, _("On the IP range's VLAN of the machine")),
        (DEFINED, _("Preset in 'VLAN for machines accepted by RADIUS'")),
    )

    radius_general_policy = models.CharField(
        max_length=32,
        choices=CHOICE_RADIUS,
        default='DEFINED'
    )
    vlan_decision_ok = models.OneToOneField(
        'machines.Vlan',
        on_delete=models.PROTECT,
        related_name='decision_ok',
        blank=True,
        null=True
    )
    vlan_decision_nok = models.OneToOneField(
        'machines.Vlan',
        on_delete=models.PROTECT,
        related_name='decision_nok',
        blank=True,
        null=True
    )

    class Meta:
        permissions = (
            ("view_optionaltopologie", _("Can view the topology options")),
        )
        verbose_name = _("topology options")


@receiver(post_save, sender=OptionalTopologie)
def optionaltopologie_post_save(**kwargs):
    """Ecriture dans le cache"""
    topologie_pref = kwargs['instance']
    topologie_pref.set_in_cache()


class GeneralOption(AclMixin, PreferencesModel):
    """Options générales : nombre de resultats par page, nom du site,
    temps où les liens sont valides"""

    general_message_fr = models.TextField(
        default="",
        blank=True,
        help_text=_("General message displayed on the French version of the"
                    " website (e.g. in case of maintenance)")
    )
    general_message_en = models.TextField(
        default="",
        blank=True,
        help_text=_("General message displayed on the English version of the"
                    " website (e.g. in case of maintenance)")
    )
    search_display_page = models.IntegerField(default=15)
    pagination_number = models.IntegerField(default=25)
    pagination_large_number = models.IntegerField(default=8)
    req_expire_hrs = models.IntegerField(default=48)
    site_name = models.CharField(max_length=32, default="Re2o")
    email_from = models.EmailField(default="www-data@example.com")
    GTU_sum_up = models.TextField(
        default="",
        blank=True,
    )
    GTU = models.FileField(
        upload_to='',
        default="",
        null=True,
        blank=True,
    )

    class Meta:
        permissions = (
            ("view_generaloption", _("Can view the general options")),
        )
        verbose_name = _("general options")


@receiver(post_save, sender=GeneralOption)
def generaloption_post_save(**kwargs):
    """Ecriture dans le cache"""
    general_pref = kwargs['instance']
    general_pref.set_in_cache()


class Service(AclMixin, models.Model):
    """Liste des services affichés sur la page d'accueil : url, description,
    image et nom"""
    name = models.CharField(max_length=32)
    url = models.URLField()
    description = models.TextField()
    image = models.ImageField(upload_to='logo', blank=True)

    class Meta:
        permissions = (
            ("view_service", _("Can view the service options")),
        )
        verbose_name = _("service")
        verbose_name_plural =_("services")

    def __str__(self):
        return str(self.name)

class MailContact(AclMixin, models.Model):
    """Contact email adress with a commentary."""

    address = models.EmailField(
        default = "contact@example.org",
        help_text = _("Contact email address")
    )

    commentary = models.CharField(
        blank = True,
        null = True,
        help_text = _(
            "Description of the associated email address."),
        max_length = 256
    )

    @cached_property
    def get_name(self):
        return self.address.split("@")[0]

    class Meta:
        permissions = (
            ("view_mailcontact", _("Can view a contact email address object")),
        )
        verbose_name = _("contact email address")
        verbose_name_plural = _("contact email addresses")

    def __str__(self):
        return(self.address)


class AssoOption(AclMixin, PreferencesModel):
    """Options générales de l'asso : siret, addresse, nom, etc"""

    name = models.CharField(
        default=_("Networking organisation school Something"),
        max_length=256
    )
    siret = models.CharField(default="00000000000000", max_length=32)
    adresse1 = models.CharField(default=_("Threadneedle Street"), max_length=128)
    adresse2 = models.CharField(default=_("London EC2R 8AH"), max_length=128)
    contact = models.EmailField(default="contact@example.org")
    telephone = models.CharField(max_length=15, default="0000000000")
    pseudo = models.CharField(default=_("Organisation"), max_length=32)
    utilisateur_asso = models.OneToOneField(
        'users.User',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    description = models.TextField(
        null=True,
        blank=True,
    )

    class Meta:
        permissions = (
            ("view_assooption", _("Can view the organisation options")),
        )
        verbose_name = _("organisation options")


@receiver(post_save, sender=AssoOption)
def assooption_post_save(**kwargs):
    """Ecriture dans le cache"""
    asso_pref = kwargs['instance']
    asso_pref.set_in_cache()


class HomeOption(AclMixin, PreferencesModel):
    """Settings of the home page (facebook/twitter etc)"""

    facebook_url = models.URLField(
        null=True,
        blank=True
    )
    twitter_url = models.URLField(
        null=True,
        blank=True
    )
    twitter_account_name = models.CharField(
        max_length=32,
        null=True,
        blank=True
    )

    class Meta:
        permissions = (
            ("view_homeoption", _("Can view the homepage options")),
        )
        verbose_name = _("homepage options")


@receiver(post_save, sender=HomeOption)
def homeoption_post_save(**kwargs):
    """Ecriture dans le cache"""
    home_pref = kwargs['instance']
    home_pref.set_in_cache()


class MailMessageOption(AclMixin, models.Model):
    """Reglages, mail de bienvenue et autre"""

    welcome_mail_fr = models.TextField(default="")
    welcome_mail_en = models.TextField(default="")

    class Meta:
        permissions = (
            ("view_mailmessageoption", _("Can view the email message"
                                         " options")),
        )
        verbose_name = _("email message options")

