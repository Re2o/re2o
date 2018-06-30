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
    PRETTY_NAME = "Options utilisateur"

    is_tel_mandatory = models.BooleanField(default=True)
    gpg_fingerprint = models.BooleanField(default=True)
    all_can_create_club = models.BooleanField(
        default=False,
        help_text="Les users peuvent créer un club"
    )
    all_can_create_adherent = models.BooleanField(
        default=False,
        help_text="Les users peuvent créer d'autres adhérents",
    )
    self_adhesion = models.BooleanField(
        default=False,
        help_text="Un nouvel utilisateur peut se créer son compte sur re2o"
    )
    shell_default = models.OneToOneField(
        'users.ListShell',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    local_email_accounts_enabled = models.BooleanField(
        default=False,
        help_text="Enable local email accounts for users"
    )
    local_email_domain = models.CharField(
        max_length = 32,
        default = "@example.org",
        help_text="Domain to use for local email accounts",
    )
    max_email_address = models.IntegerField(
        default = 15,
        help_text = "Maximum number of local email address for a standard user"
    )

    class Meta:
        permissions = (
            ("view_optionaluser", "Peut voir les options de l'user"),
        )

    def clean(self):
        """Clean model:
        Check the mail_extension
        """
        if self.local_email_domain[0] != "@":
            raise ValidationError("Mail domain must begin with @")


@receiver(post_save, sender=OptionalUser)
def optionaluser_post_save(**kwargs):
    """Ecriture dans le cache"""
    user_pref = kwargs['instance']
    user_pref.set_in_cache()


class OptionalMachine(AclMixin, PreferencesModel):
    """Options pour les machines : maximum de machines ou d'alias par user
    sans droit, activation de l'ipv6"""
    PRETTY_NAME = "Options machines"

    SLAAC = 'SLAAC'
    DHCPV6 = 'DHCPV6'
    DISABLED = 'DISABLED'
    CHOICE_IPV6 = (
        (SLAAC, 'Autoconfiguration par RA'),
        (DHCPV6, 'Attribution des ip par dhcpv6'),
        (DISABLED, 'Désactivé'),
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
        default=True,
        help_text="Permet à l'user de créer une machine"
    )

    @cached_property
    def ipv6(self):
        """ Check if the IPv6 option is activated """
        return not self.get_cached_value('ipv6_mode') == 'DISABLED'

    class Meta:
        permissions = (
            ("view_optionalmachine", "Peut voir les options de machine"),
        )


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
    PRETTY_NAME = "Options topologie"
    MACHINE = 'MACHINE'
    DEFINED = 'DEFINED'
    CHOICE_RADIUS = (
        (MACHINE, 'Sur le vlan de la plage ip machine'),
        (DEFINED, 'Prédéfini dans "Vlan où placer les machines\
            après acceptation RADIUS"'),
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
            ("view_optionaltopologie", "Peut voir les options de topologie"),
        )


@receiver(post_save, sender=OptionalTopologie)
def optionaltopologie_post_save(**kwargs):
    """Ecriture dans le cache"""
    topologie_pref = kwargs['instance']
    topologie_pref.set_in_cache()


class GeneralOption(AclMixin, PreferencesModel):
    """Options générales : nombre de resultats par page, nom du site,
    temps où les liens sont valides"""
    PRETTY_NAME = "Options générales"

    general_message = models.TextField(
        default="",
        blank=True,
        help_text="Message général affiché sur le site (maintenance, etc"
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
            ("view_generaloption", "Peut voir les options générales"),
        )


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
            ("view_service", "Peut voir les options de service"),
        )

    def __str__(self):
        return str(self.name)

class MailContact(AclMixin, models.Model):
    """Addresse mail de contact associée à un commentaire descriptif"""

    address = models.EmailField(
        default = "contact@example.org",
        help_text = "Adresse mail de contact"
    )

    commentary = models.CharField(
        blank = True,
        null = True,
        help_text = "Description de l'utilisation de l'adresse mail associée",
        max_length = 256
    )

    class Meta:
        permissions = (
            ("view_mailcontact", "Peut voir les mails de contact"),
        )

    def __str__(self):
        return(self.address)


class AssoOption(AclMixin, PreferencesModel):
    """Options générales de l'asso : siret, addresse, nom, etc"""
    PRETTY_NAME = "Options de l'association"

    name = models.CharField(
        default="Association réseau école machin",
        max_length=256
    )
    siret = models.CharField(default="00000000000000", max_length=32)
    adresse1 = models.CharField(default="1 Rue de exemple", max_length=128)
    adresse2 = models.CharField(default="94230 Cachan", max_length=128)
    contact = models.EmailField(default="contact@example.org")
    telephone = models.CharField(max_length=15, default="0000000000")
    pseudo = models.CharField(default="Asso", max_length=32)
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
            ("view_assooption", "Peut voir les options de l'asso"),
        )


@receiver(post_save, sender=AssoOption)
def assooption_post_save(**kwargs):
    """Ecriture dans le cache"""
    asso_pref = kwargs['instance']
    asso_pref.set_in_cache()


class HomeOption(AclMixin, PreferencesModel):
    """Settings of the home page (facebook/twitter etc)"""
    PRETTY_NAME = "Options de la page d'accueil"

    facebook_url = models.URLField(
        null=True,
        blank=True,
        help_text="Url du compte facebook"
    )
    twitter_url = models.URLField(
        null=True,
        blank=True,
        help_text="Url du compte twitter"
    )
    twitter_account_name = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text="Nom du compte à afficher"
    )

    class Meta:
        permissions = (
            ("view_homeoption", "Peut voir les options de l'accueil"),
        )


@receiver(post_save, sender=HomeOption)
def homeoption_post_save(**kwargs):
    """Ecriture dans le cache"""
    home_pref = kwargs['instance']
    home_pref.set_in_cache()


class MailMessageOption(AclMixin, models.Model):
    """Reglages, mail de bienvenue et autre"""
    PRETTY_NAME = "Options de corps de mail"

    welcome_mail_fr = models.TextField(default="")
    welcome_mail_en = models.TextField(default="")

    class Meta:
        permissions = (
            ("view_mailmessageoption", "Peut voir les options de mail"),
        )
