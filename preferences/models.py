# -*- mode: python; coding: utf-8 -*-
# Re2o un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
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
import os

from django.utils.functional import cached_property
from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

import machines.models

from re2o.mixins import AclMixin, RevMixin
from re2o.aes_field import AESEncryptedField

from datetime import timedelta


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

    DISABLED = "DISABLED"
    ONLY_INACTIVE = "ONLY_INACTIVE"
    ALL_ROOM = "ALL_ROOM"
    ROOM_POLICY = (
        (DISABLED, _("Users can't select their room")),
        (ONLY_INACTIVE, _("Users can only select a room occupied by a user with a disabled connection.")),
        (ALL_ROOM, _("Users can select all rooms")),
    )

    is_tel_mandatory = models.BooleanField(default=True)
    gpg_fingerprint = models.BooleanField(default=True)
    all_can_create_club = models.BooleanField(
        default=False, help_text=_("Users can create a club.")
    )
    all_can_create_adherent = models.BooleanField(
        default=False, help_text=_("Users can create a member.")
    )
    shell_default = models.OneToOneField(
        "users.ListShell", on_delete=models.PROTECT, blank=True, null=True
    )
    self_change_shell = models.BooleanField(
        default=False, help_text=_("Users can edit their shell.")
    )
    self_room_policy = models.CharField(
        max_length=32,
        choices=ROOM_POLICY,
        default="DISABLED",
        help_text=_("Policy on self users room edition")
    )
    local_email_accounts_enabled = models.BooleanField(
        default=False, help_text=_("Enable local email accounts for users.")
    )
    local_email_domain = models.CharField(
        max_length=32,
        default="@example.org",
        help_text=_("Domain to use for local email accounts."),
    )
    max_email_address = models.IntegerField(
        default=15,
        help_text=_("Maximum number of local email addresses for a standard user."),
    )
    delete_notyetactive = models.IntegerField(
        default=15,
        help_text=_(
            "Not yet active users will be deleted after this number of days."
        ),
    )
    disable_emailnotyetconfirmed = models.IntegerField(
        default=2,
        help_text=_(
            "Users with an email address not yet confirmed will be disabled after this number of days."
        ),
    )
    self_adhesion = models.BooleanField(
        default=False, help_text=_("A new user can create their account on Re2o.")
    )
    all_users_active = models.BooleanField(
        default=False,
        help_text=_(
            "If True, all new created and connected users are active."
            " If False, only when a valid registration has been paid."
        ),
    )
    allow_set_password_during_user_creation = models.BooleanField(
        default=False,
        help_text=_(
            "If True, users have the choice to receive an email containing"
            " a link to reset their password during creation, or to directly"
            " set their password in the page."
            " If False, an email is always sent."
        ),
    )
    allow_archived_connexion = models.BooleanField(
        default=False, help_text=_("If True, archived users are allowed to connect.")
    )

    class Meta:
        permissions = (("view_optionaluser", _("Can view the user preferences")),)
        verbose_name = _("user preferences")

    def clean(self):
        """Clean model:
        Check the mail_extension
        """
        if self.local_email_domain[0] != "@":
            raise ValidationError(_("Email domain must begin with @."))


@receiver(post_save, sender=OptionalUser)
def optionaluser_post_save(**kwargs):
    """Ecriture dans le cache"""
    user_pref = kwargs["instance"]
    user_pref.set_in_cache()


class OptionalMachine(AclMixin, PreferencesModel):
    """Options pour les machines : maximum de machines ou d'alias par user
    sans droit, activation de l'ipv6"""

    SLAAC = "SLAAC"
    DHCPV6 = "DHCPV6"
    DISABLED = "DISABLED"
    CHOICE_IPV6 = (
        (SLAAC, _("Automatic configuration by RA")),
        (DHCPV6, _("IP addresses assignment by DHCPv6")),
        (DISABLED, _("Disabled")),
    )

    password_machine = models.BooleanField(default=False)
    max_lambdauser_interfaces = models.IntegerField(default=10)
    max_lambdauser_aliases = models.IntegerField(default=10)
    ipv6_mode = models.CharField(max_length=32, choices=CHOICE_IPV6, default="DISABLED")
    create_machine = models.BooleanField(default=True)
    default_dns_ttl = models.PositiveIntegerField(
        verbose_name=_("default Time To Live (TTL) for CNAME, A and AAAA records"),
        default=172800,  # 2 days
    )

    @cached_property
    def ipv6(self):
        """ Check if the IPv6 option is activated """
        return not self.get_cached_value("ipv6_mode") == "DISABLED"

    class Meta:
        permissions = (("view_optionalmachine", _("Can view the machine preferences")),)
        verbose_name = _("machine preferences")


@receiver(post_save, sender=OptionalMachine)
def optionalmachine_post_save(**kwargs):
    """Synchronisation ipv6 et ecriture dans le cache"""
    machine_pref = kwargs["instance"]
    machine_pref.set_in_cache()
    if machine_pref.ipv6_mode != "DISABLED":
        for interface in machines.models.Interface.objects.all():
            interface.sync_ipv6()


class OptionalTopologie(AclMixin, PreferencesModel):
    """Reglages pour la topologie : mode d'accès radius, vlan où placer
    les machines en accept ou reject"""

    MACHINE = "MACHINE"
    DEFINED = "DEFINED"
    CHOICE_RADIUS = (
        (MACHINE, _("On the IP range's VLAN of the machine")),
        (DEFINED, _("Preset in \"VLAN for machines accepted by RADIUS\"")),
    )
    CHOICE_PROVISION = (("sftp", "SFTP"), ("tftp", "TFTP"))

    switchs_web_management = models.BooleanField(
        default=False,
        help_text=_("Web management, activated in case of automatic provision."),
    )
    switchs_web_management_ssl = models.BooleanField(
        default=False,
        help_text=_(
            "SSL web management, make sure that a certificate is"
            " installed on the switch."
        ),
    )
    switchs_rest_management = models.BooleanField(
        default=False,
        help_text=_("REST management, activated in case of automatic provision."),
    )
    switchs_ip_type = models.OneToOneField(
        "machines.IpType",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_("IP range for the management of switches."),
    )
    switchs_provision = models.CharField(
        max_length=32,
        choices=CHOICE_PROVISION,
        default="tftp",
        help_text=_("Provision of configuration mode for switches."),
    )
    sftp_login = models.CharField(
        max_length=32, null=True, blank=True, help_text=_("SFTP login for switches.")
    )
    sftp_pass = AESEncryptedField(
        max_length=63, null=True, blank=True, help_text=_("SFTP password.")
    )

    @cached_property
    def provisioned_switchs(self):
        """Liste des switches provisionnés"""
        from topologie.models import Switch

        return Switch.objects.filter(automatic_provision=True).order_by(
            "interface__domain__name"
        )

    @cached_property
    def switchs_management_interface(self):
        """Return the ip of the interface that the switch have to contact to get it's config"""
        if self.switchs_ip_type:
            from machines.models import Role, Interface

            return (
                Interface.objects.filter(
                    machine__interface__in=Role.interface_for_roletype(
                        "switch-conf-server"
                    )
                )
                .filter(machine_type__ip_type=self.switchs_ip_type)
                .first()
            )
        else:
            return None

    @cached_property
    def switchs_management_interface_ip(self):
        """Same, but return the ipv4"""
        if not self.switchs_management_interface:
            return None
        return self.switchs_management_interface.ipv4

    @cached_property
    def switchs_management_sftp_creds(self):
        """Credentials des switchs pour provion sftp"""
        if self.sftp_login and self.sftp_pass:
            return {"login": self.sftp_login, "pass": self.sftp_pass}
        else:
            return None

    @cached_property
    def switchs_management_utils(self):
        """Used for switch_conf, return a list of ip on vlans"""
        from machines.models import Role, Ipv6List, Interface

        def return_ips_dict(interfaces):
            return {
                "ipv4": [str(interface.ipv4) for interface in interfaces],
                "ipv6": Ipv6List.objects.filter(interface__in=interfaces).values_list(
                    "ipv6", flat=True
                ),
            }

        ntp_servers = Role.all_interfaces_for_roletype("ntp-server").filter(
            machine_type__ip_type=self.switchs_ip_type
        )
        log_servers = Role.all_interfaces_for_roletype("log-server").filter(
            machine_type__ip_type=self.switchs_ip_type
        )
        radius_servers = Role.all_interfaces_for_roletype("radius-server").filter(
            machine_type__ip_type=self.switchs_ip_type
        )
        dhcp_servers = Role.all_interfaces_for_roletype("dhcp-server")
        dns_recursive_servers = Role.all_interfaces_for_roletype(
            "dns-recursive-server"
        ).filter(machine_type__ip_type=self.switchs_ip_type)
        subnet = None
        subnet6 = None
        if self.switchs_ip_type:
            subnet = (
                self.switchs_ip_type.ip_net_full_info
                or self.switchs_ip_type.ip_set_full_info[0]
            )
            subnet6 = self.switchs_ip_type.ip6_set_full_info
        return {
            "ntp_servers": return_ips_dict(ntp_servers),
            "log_servers": return_ips_dict(log_servers),
            "radius_servers": return_ips_dict(radius_servers),
            "dhcp_servers": return_ips_dict(dhcp_servers),
            "dns_recursive_servers": return_ips_dict(dns_recursive_servers),
            "subnet": subnet,
            "subnet6": subnet6,
        }

    @cached_property
    def provision_switchs_enabled(self):
        """Return true if all settings are ok : switchs on automatic provision,
        ip_type"""
        return bool(
            self.provisioned_switchs
            and self.switchs_ip_type
            and SwitchManagementCred.objects.filter(default_switch=True).exists()
            and self.switchs_management_interface_ip
            and bool(
                self.switchs_provision != "sftp" or self.switchs_management_sftp_creds
            )
        )

    class Meta:
        permissions = (("view_optionaltopologie", _("Can view the topology preferences")),)
        verbose_name = _("topology preferences")


@receiver(post_save, sender=OptionalTopologie)
def optionaltopologie_post_save(**kwargs):
    """Ecriture dans le cache"""
    topologie_pref = kwargs["instance"]
    topologie_pref.set_in_cache()


class RadiusKey(AclMixin, models.Model):
    """Class of a radius key"""

    radius_key = AESEncryptedField(max_length=255, help_text=_("RADIUS key."))
    comment = models.CharField(
        max_length=255, null=True, blank=True, help_text=_("Comment for this key.")
    )
    default_switch = models.BooleanField(
        default=False, help_text=_("Default key for switches.")
    )

    class Meta:
        permissions = (("view_radiuskey", _("Can view a RADIUS key object")),)
        verbose_name = _("RADIUS key")
        verbose_name_plural = _("RADIUS keys")

    def clean(self):
        """Clean model:
        Check default switch is unique
        """
        if RadiusKey.objects.filter(default_switch=True).count() > 1:
            raise ValidationError(_("Default RADIUS key for switches already exists."))

    def __str__(self):
        return _("RADIUS key ") + str(self.id) + " " + str(self.comment)


class SwitchManagementCred(AclMixin, models.Model):
    """Class of a management creds of a switch, for rest management"""

    management_id = models.CharField(max_length=63, help_text=_("Switch login."))
    management_pass = AESEncryptedField(max_length=63, help_text=_("Password."))
    default_switch = models.BooleanField(
        default=True, unique=True, help_text=_("Default credentials for switches.")
    )

    class Meta:
        permissions = (
            (
                "view_switchmanagementcred",
                _("Can view a switch management credentials object"),
            ),
        )
        verbose_name = _("switch management credentials")

    def __str__(self):
        return _("Switch login ") + str(self.management_id)


class Reminder(AclMixin, models.Model):
    """Options pour les mails de notification de fin d'adhésion.
    Days: liste des nombres de jours pour lesquells un mail est envoyé
    optionalMessage: message additionel pour le mail
    """

    days = models.IntegerField(
        default=7,
        unique=True,
        help_text=_("Delay between the email and the membership's end."),
    )
    message = models.TextField(
        default="",
        null=True,
        blank=True,
        help_text=_("Message displayed specifically for this reminder."),
    )

    class Meta:
        permissions = (("view_reminder", _("Can view a reminder object")),)
        verbose_name = _("reminder")
        verbose_name_plural = _("reminders")

    def users_to_remind(self):
        from re2o.utils import all_has_access

        date = timezone.now().replace(minute=0, hour=0)
        futur_date = date + timedelta(days=self.days)
        users = all_has_access(futur_date).exclude(
            pk__in=all_has_access(futur_date + timedelta(days=1))
        )
        return users


class GeneralOption(AclMixin, PreferencesModel):
    """Options générales : nombre de resultats par page, nom du site,
    temps où les liens sont valides"""

    general_message_fr = models.TextField(
        default="",
        blank=True,
        help_text=_(
            "General message displayed on the French version of the"
            " website (e.g. in case of maintenance)."
        ),
    )
    general_message_en = models.TextField(
        default="",
        blank=True,
        help_text=_(
            "General message displayed on the English version of the"
            " website (e.g. in case of maintenance)."
        ),
    )
    search_display_page = models.IntegerField(default=15)
    pagination_number = models.IntegerField(default=25)
    pagination_large_number = models.IntegerField(default=8)
    req_expire_hrs = models.IntegerField(default=48)
    site_name = models.CharField(max_length=32, default="Re2o")
    email_from = models.EmailField(default="www-data@example.com")
    main_site_url = models.URLField(max_length=255, default="http://re2o.example.org")
    GTU_sum_up = models.TextField(default="", blank=True)
    GTU = models.FileField(upload_to="", default="", null=True, blank=True)

    class Meta:
        permissions = (("view_generaloption", _("Can view the general preferences")),)
        verbose_name = _("general preferences")


@receiver(post_save, sender=GeneralOption)
def generaloption_post_save(**kwargs):
    """Ecriture dans le cache"""
    general_pref = kwargs["instance"]
    general_pref.set_in_cache()


class Service(AclMixin, models.Model):
    """Liste des services affichés sur la page d'accueil : url, description,
    image et nom"""

    name = models.CharField(max_length=32)
    url = models.URLField()
    description = models.TextField()
    image = models.ImageField(upload_to="logo", blank=True)

    class Meta:
        permissions = (("view_service", _("Can view the service preferences")),)
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self):
        return str(self.name)


class MailContact(AclMixin, models.Model):
    """Contact email adress with a commentary."""

    address = models.EmailField(
        default="contact@example.org", help_text=_("Contact email address.")
    )

    commentary = models.CharField(
        blank=True,
        null=True,
        help_text=_("Description of the associated email address."),
        max_length=256,
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
        return self.address


class Mandate(RevMixin, AclMixin, models.Model):
    class Meta:
        verbose_name = _("mandate")
        verbose_name_plural = _("mandates")
        permissions = (("view_mandate", _("Can view a mandate object")),)

    president = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("president of the association"),
        help_text=_("Displayed on subscription vouchers."),
    )
    start_date = models.DateTimeField(verbose_name=_("start date"))
    end_date = models.DateTimeField(verbose_name=_("end date"), blank=True, null=True)

    @classmethod
    def get_mandate(cls, date=timezone.now):
        """"Find the mandate taking place at the given date."""
        if callable(date):
            date = date()
        mandate = (
            cls.objects.exclude(end_date__lte=date).order_by("start_date").first()
            or cls.objects.order_by("start_date").last()
        )
        if not mandate:
            raise cls.DoesNotExist(
                _("No mandates have been created. Please go to the preferences page to create one.")
            )
        return mandate

    def is_over(self):
        return self.end_date is None

    def __str__(self):
        return str(self.president) + " " + str(self.start_date.year)


class AssoOption(AclMixin, PreferencesModel):
    """Options générales de l'asso : siret, addresse, nom, etc"""

    name = models.CharField(
        default=_("Networking organisation school Something"), max_length=256
    )
    siret = models.CharField(default="00000000000000", max_length=32)
    adresse1 = models.CharField(default=_("Threadneedle Street"), max_length=128)
    adresse2 = models.CharField(default=_("London EC2R 8AH"), max_length=128)
    contact = models.EmailField(default="contact@example.org")
    telephone = models.CharField(max_length=15, default="0000000000")
    pseudo = models.CharField(default=_("Organisation"), max_length=32)
    utilisateur_asso = models.OneToOneField(
        "users.User", on_delete=models.PROTECT, blank=True, null=True
    )
    description = models.TextField(null=True, blank=True)

    class Meta:
        permissions = (("view_assooption", _("Can view the organisation preferences")),)
        verbose_name = _("organisation preferences")


@receiver(post_save, sender=AssoOption)
def assooption_post_save(**kwargs):
    """Ecriture dans le cache"""
    asso_pref = kwargs["instance"]
    asso_pref.set_in_cache()


class HomeOption(AclMixin, PreferencesModel):
    """Settings of the home page (facebook/twitter etc)"""

    facebook_url = models.URLField(null=True, blank=True)
    twitter_url = models.URLField(null=True, blank=True)
    twitter_account_name = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        permissions = (("view_homeoption", _("Can view the homepage preferences")),)
        verbose_name = _("homepage preferences")


@receiver(post_save, sender=HomeOption)
def homeoption_post_save(**kwargs):
    """Ecriture dans le cache"""
    home_pref = kwargs["instance"]
    home_pref.set_in_cache()


class MailMessageOption(AclMixin, models.Model):
    """Reglages, mail de bienvenue et autre"""

    welcome_mail_fr = models.TextField(
        default="", blank=True, help_text=_("Welcome email in French.")
    )
    welcome_mail_en = models.TextField(
        default="", blank=True, help_text=_("Welcome email in English.")
    )

    class Meta:
        permissions = (
            ("view_mailmessageoption", _("Can view the email message preferences")),
        )
        verbose_name = _("email message preferences")


class RadiusAttribute(RevMixin, AclMixin, models.Model):
    class Meta:
        verbose_name = _("RADIUS attribute")
        verbose_name_plural = _("RADIUS attributes")

    attribute = models.CharField(
        max_length=255,
        verbose_name=_("attribute"),
        help_text=_("See https://freeradius.org/rfc/attributes.html."),
    )
    value = models.CharField(max_length=255, verbose_name=_("value"))
    comment = models.TextField(
        verbose_name=_("comment"),
        help_text=_("Use this field to document this attribute."),
        blank=True,
        default="",
    )

    def __str__(self):
        return " ".join([self.attribute, "=", self.value])


class RadiusOption(AclMixin, PreferencesModel):
    class Meta:
        verbose_name = _("RADIUS policy")
        verbose_name_plural = _("RADIUS policies")

    MACHINE = "MACHINE"
    DEFINED = "DEFINED"
    CHOICE_RADIUS = (
        (MACHINE, _("On the IP range's VLAN of the machine")),
        (DEFINED, _("Preset in \"VLAN for machines accepted by RADIUS\"")),
    )
    REJECT = "REJECT"
    SET_VLAN = "SET_VLAN"
    CHOICE_POLICY = (
        (REJECT, _("Reject the machine")),
        (SET_VLAN, _("Place the machine on the VLAN")),
    )
    radius_general_policy = models.CharField(
        max_length=32, choices=CHOICE_RADIUS, default="DEFINED"
    )
    unknown_machine = models.CharField(
        max_length=32,
        choices=CHOICE_POLICY,
        default=REJECT,
        verbose_name=_("policy for unknown machines"),
    )
    unknown_machine_vlan = models.ForeignKey(
        "machines.Vlan",
        on_delete=models.PROTECT,
        related_name="unknown_machine_vlan",
        blank=True,
        null=True,
        verbose_name=_("unknown machines VLAN"),
        help_text=_("VLAN for unknown machines if not rejected."),
    )
    unknown_machine_attributes = models.ManyToManyField(
        RadiusAttribute,
        related_name="unknown_machine_attribute",
        blank=True,
        verbose_name=_("unknown machines attributes"),
        help_text=_("Answer attributes for unknown machines."),
    )
    unknown_port = models.CharField(
        max_length=32,
        choices=CHOICE_POLICY,
        default=REJECT,
        verbose_name=_("policy for unknown ports"),
    )
    unknown_port_vlan = models.ForeignKey(
        "machines.Vlan",
        on_delete=models.PROTECT,
        related_name="unknown_port_vlan",
        blank=True,
        null=True,
        verbose_name=_("unknown ports VLAN"),
        help_text=_("VLAN for unknown ports if not rejected."),
    )
    unknown_port_attributes = models.ManyToManyField(
        RadiusAttribute,
        related_name="unknown_port_attribute",
        blank=True,
        verbose_name=_("unknown ports attributes"),
        help_text=_("Answer attributes for unknown ports."),
    )
    unknown_room = models.CharField(
        max_length=32,
        choices=CHOICE_POLICY,
        default=REJECT,
        verbose_name=_(
            "Policy for machines connecting from unregistered rooms"
            " (relevant on ports with STRICT RADIUS mode)"
        ),
    )
    unknown_room_vlan = models.ForeignKey(
        "machines.Vlan",
        related_name="unknown_room_vlan",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("unknown rooms VLAN"),
        help_text=_("VLAN for unknown rooms if not rejected."),
    )
    unknown_room_attributes = models.ManyToManyField(
        RadiusAttribute,
        related_name="unknown_room_attribute",
        blank=True,
        verbose_name=_("unknown rooms attributes"),
        help_text=_("Answer attributes for unknown rooms."),
    )
    non_member = models.CharField(
        max_length=32,
        choices=CHOICE_POLICY,
        default=REJECT,
        verbose_name=_("policy for non members"),
    )
    non_member_vlan = models.ForeignKey(
        "machines.Vlan",
        related_name="non_member_vlan",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("non members VLAN"),
        help_text=_("VLAN for non members if not rejected."),
    )
    non_member_attributes = models.ManyToManyField(
        RadiusAttribute,
        related_name="non_member_attribute",
        blank=True,
        verbose_name=_("non members attributes"),
        help_text=_("Answer attributes for non members."),
    )
    banned = models.CharField(
        max_length=32,
        choices=CHOICE_POLICY,
        default=REJECT,
        verbose_name=_("policy for banned users"),
    )
    banned_vlan = models.ForeignKey(
        "machines.Vlan",
        related_name="banned_vlan",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("banned users VLAN"),
        help_text=_("VLAN for banned users if not rejected."),
    )
    banned_attributes = models.ManyToManyField(
        RadiusAttribute,
        related_name="banned_attribute",
        blank=True,
        verbose_name=_("banned users attributes"),
        help_text=_("Answer attributes for banned users."),
    )
    vlan_decision_ok = models.OneToOneField(
        "machines.Vlan",
        on_delete=models.PROTECT,
        related_name="vlan_ok_option",
        blank=True,
        null=True,
    )
    ok_attributes = models.ManyToManyField(
        RadiusAttribute,
        related_name="ok_attribute",
        blank=True,
        verbose_name=_("accepted users attributes"),
        help_text=_("Answer attributes for accepted users."),
    )

    @classmethod
    def get_attributes(cls, name, attribute_kwargs={}):
        return (
            (str(attribute.attribute), str(attribute.value % attribute_kwargs))
            for attribute in cls.get_cached_value(name).all()
        )


def default_invoice():
    tpl, _ = DocumentTemplate.objects.get_or_create(
        name="Re2o default invoice", template="templates/default_invoice.tex"
    )
    return tpl.id


def default_voucher():
    tpl, _ = DocumentTemplate.objects.get_or_create(
        name="Re2o default voucher", template="templates/default_voucher.tex"
    )
    return tpl.id


class CotisationsOption(AclMixin, PreferencesModel):
    class Meta:
        verbose_name = _("subscription preferences")

    invoice_template = models.OneToOneField(
        "preferences.DocumentTemplate",
        verbose_name=_("template for invoices"),
        related_name="invoice_template",
        on_delete=models.PROTECT,
        default=default_invoice,
    )
    voucher_template = models.OneToOneField(
        "preferences.DocumentTemplate",
        verbose_name=_("template for subscription vouchers"),
        related_name="voucher_template",
        on_delete=models.PROTECT,
        default=default_voucher,
    )
    send_voucher_mail = models.BooleanField(
        verbose_name=_("send voucher by email when the invoice is controlled"),
        help_text=_(
            "Be careful, if no mandate is defined on the preferences page,"
            " errors will be triggered when generating vouchers."
        ),
        default=False,
    )


class DocumentTemplate(RevMixin, AclMixin, models.Model):
    """Represent a template in order to create documents such as invoice or
    subscription voucher.
    """

    template = models.FileField(upload_to="templates/", verbose_name=_("template"))
    name = models.CharField(max_length=125, verbose_name=_("name"), unique=True)

    class Meta:
        verbose_name = _("document template")
        verbose_name_plural = _("document templates")

    def __str__(self):
        return str(self.name)


@receiver(models.signals.post_delete, sender=DocumentTemplate)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `DocumentTemplate` object is deleted.
    """
    if instance.template:
        if os.path.isfile(instance.template.path):
            os.remove(instance.template.path)


@receiver(models.signals.pre_save, sender=DocumentTemplate)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `DocumentTemplate` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = DocumentTemplate.objects.get(pk=instance.pk).template
    except DocumentTemplate.DoesNotExist:
        return False

    new_file = instance.template
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
