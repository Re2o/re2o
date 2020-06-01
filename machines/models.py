# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2016-2018  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2018  Charlie Jacomme
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
"""machines.models
The models definitions for the Machines app
"""

from __future__ import unicode_literals

import base64
import hashlib
import re
from datetime import timedelta
from ipaddress import IPv6Address
from itertools import chain

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms import ValidationError
from django.utils import timezone
from django.db import transaction
from reversion import revisions as reversion
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from macaddress.fields import MACAddressField, default_dialect
from netaddr import (
    mac_bare,
    EUI,
    NotRegisteredError,
    IPSet,
    IPRange,
    IPNetwork,
    IPAddress,
)

import preferences.models
import users.models
from re2o.field_permissions import FieldPermissionModelMixin
from re2o.mixins import AclMixin, RevMixin


class Machine(RevMixin, FieldPermissionModelMixin, AclMixin, models.Model):
    """ Class définissant une machine, object parent user, objets fils
    interfaces"""

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    name = models.CharField(
        max_length=255, help_text=_("Optional."), blank=True, null=True
    )
    active = models.BooleanField(default=True)

    class Meta:
        permissions = (
            ("view_machine", _("Can view a machine object")),
            ("change_machine_user", _("Can change the user of a machine")),
        )
        verbose_name = _("machine")
        verbose_name_plural = _("machines")

    def linked_objects(self):
        """Return linked objects : machine and domain.
        Usefull in history display"""
        return chain(
            self.interface_set.all(),
            Domain.objects.filter(interface_parent__in=self.interface_set.all()),
        )

    @staticmethod
    def can_change_user(user_request, *_args, **_kwargs):
        """Checks if an user is allowed to change the user who owns a
        Machine.

        Args:
            user_request: The user requesting to change owner.

        Returns:
            A tuple with a boolean stating if edition is allowed and an
            explanation message.
        """
        can = user_request.has_perm("machines.change_machine_user")
        return (
            can,
            _("You don't have the right to change the machine's user.")
            if not can
            else None,
            ("machines.change_machine_user",),
        )

    @staticmethod
    def can_view_all(user_request, *_args, **_kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des machines,
        droit particulier correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm("machines.view_machine"):
            return (
                False,
                _("You don't have the right to view all the machines."),
                ("machines.view_machine",),
            )
        return True, None, None

    @staticmethod
    def can_create(user_request, userid, *_args, **_kwargs):
        """Vérifie qu'un user qui fait la requète peut bien créer la machine
        et n'a pas atteint son quota, et crée bien une machine à lui
        :param user_request: Utilisateur qui fait la requête
        :param userid: id de l'user dont on va créer une machine
        :return: soit True, soit False avec la raison de l'échec"""
        try:
            user = users.models.User.objects.get(pk=userid)
        except users.models.User.DoesNotExist:
            return False, _("Nonexistent user."), None
        max_lambdauser_interfaces = preferences.models.OptionalMachine.get_cached_value(
            "max_lambdauser_interfaces"
        )
        if not user_request.has_perm("machines.add_machine"):
            if not (
                preferences.models.OptionalMachine.get_cached_value("create_machine")
            ):
                return (
                    False,
                    _("You don't have the right to add a machine."),
                    ("machines.add_machine",),
                )
            if user != user_request:
                return (
                    False,
                    _("You don't have the right to add a machine to another" " user."),
                    ("machines.add_machine",),
                )
            if user.user_interfaces().count() >= max_lambdauser_interfaces:
                return (
                    False,
                    _(
                        "You reached the maximum number of interfaces"
                        " that you are allowed to create yourself"
                        " (%s)." % max_lambdauser_interfaces
                    ),
                    None,
                )
        return True, None, None

    def can_edit(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien éditer cette instance particulière (soit
        machine de soi, soit droit particulier
        :param self: instance machine à éditer
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison le cas échéant"""
        if self.user != user_request:
            can_user, _message, permissions = self.user.can_edit(
                self.user, user_request, *args, **kwargs
            )
            if not (user_request.has_perm("machines.change_interface") and can_user):
                return (
                    False,
                    _("You don't have the right to edit a machine of another" " user."),
                    ("machines.change_interface",) + (permissions or ()),
                )
        return True, None, None

    def can_delete(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien supprimer cette instance particulière (soit
        machine de soi, soit droit particulier
        :param self: instance machine à supprimer
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if self.user != user_request:
            can_user, _message, permissions = self.user.can_edit(
                self.user, user_request, *args, **kwargs
            )
            if not (user_request.has_perm("machines.delete_interface") and can_user):
                return (
                    False,
                    _(
                        "You don't have the right to delete a machine"
                        " of another user."
                    ),
                    ("machines.change_interface",) + (permissions or ()),
                )
        return True, None, None

    def can_view(self, user_request, *_args, **_kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière (soit
        machine de soi, soit droit particulier
        :param self: instance machine à éditer
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if (
            not user_request.has_perm("machines.view_machine")
            and self.user != user_request
        ):
            return (
                False,
                _("You don't have the right to view other machines than" " yours."),
                ("machines.view_machine",),
            )
        return True, None, None

    @cached_property
    def short_name(self):
        """Par defaut, renvoie le nom de la première interface
        de cette machine"""
        interfaces_set = self.interface_set.first()
        if interfaces_set:
            return str(interfaces_set.domain.name)
        else:
            return _("No name")

    @cached_property
    def complete_name(self):
        """Par defaut, renvoie le nom de la première interface
        de cette machine"""
        return str(self.interface_set.first())

    @cached_property
    def all_short_names(self):
        """Renvoie de manière unique, le nom des interfaces de cette
        machine"""
        return (
            Domain.objects.filter(interface_parent__machine=self)
            .values_list("name", flat=True)
            .distinct()
        )

    @cached_property
    def get_name(self):
        """Return a name : user provided name or first interface name"""
        return self.name or self.short_name

    @classmethod
    def mass_delete(cls, machine_queryset):
        """Mass delete for machine queryset"""
        from topologie.models import AccessPoint

        Domain.objects.filter(
            cname__interface_parent__machine__in=machine_queryset
        )._raw_delete(machine_queryset.db)
        Domain.objects.filter(
            interface_parent__machine__in=machine_queryset
        )._raw_delete(machine_queryset.db)
        Ipv6List.objects.filter(interface__machine__in=machine_queryset)._raw_delete(
            machine_queryset.db
        )
        Interface.objects.filter(machine__in=machine_queryset).filter(
            port_lists__isnull=False
        ).delete()
        Interface.objects.filter(machine__in=machine_queryset)._raw_delete(
            machine_queryset.db
        )
        AccessPoint.objects.filter(machine_ptr__in=machine_queryset)._raw_delete(
            machine_queryset.db
        )
        machine_queryset._raw_delete(machine_queryset.db)

    @cached_property
    def all_complete_names(self):
        """Renvoie tous les tls complets de la machine"""
        return [
            str(domain)
            for domain in Domain.objects.filter(
                Q(cname__interface_parent__machine=self)
                | Q(interface_parent__machine=self)
            )
        ]

    def __init__(self, *args, **kwargs):
        super(Machine, self).__init__(*args, **kwargs)
        self.field_permissions = {"user": self.can_change_user}

    def __str__(self):
        return str(self.user) + " - " + str(self.id) + " - " + str(self.get_name)


class MachineType(RevMixin, AclMixin, models.Model):
    """ Type de machine, relié à un type d'ip, affecté aux interfaces"""

    name = models.CharField(max_length=255)
    ip_type = models.ForeignKey(
        "IpType", on_delete=models.PROTECT, blank=True, null=True
    )

    class Meta:
        permissions = (
            ("view_machinetype", _("Can view a machine type object")),
            ("use_all_machinetype", _("Can use all machine types")),
        )
        verbose_name = _("machine type")
        verbose_name_plural = _("machine types")

    def all_interfaces(self):
        """ Renvoie toutes les interfaces (cartes réseaux) de type
        machinetype"""
        return Interface.objects.filter(machine_type=self)

    @staticmethod
    def can_use_all(user_request, *_args, **_kwargs):
        """Check if an user can use every MachineType.

        Args:
            user_request: The user requesting edition.
        Returns:
            A tuple with a boolean stating if user can acces and an explanation
            message is acces is not allowed.
        """
        if not user_request.has_perm("machines.use_all_machinetype"):
            return (
                False,
                _("You don't have the right to use all machine types."),
                ("machines.use_all_machinetype",),
            )
        return True, None, None

    def __str__(self):
        return self.name


class IpType(RevMixin, AclMixin, models.Model):
    """ Type d'ip, définissant un range d'ip, affecté aux machine types"""

    name = models.CharField(max_length=255)
    extension = models.ForeignKey("Extension", on_delete=models.PROTECT)
    need_infra = models.BooleanField(default=False)
    domaine_ip_start = models.GenericIPAddressField(protocol="IPv4")
    domaine_ip_stop = models.GenericIPAddressField(protocol="IPv4")
    domaine_ip_network = models.GenericIPAddressField(
        protocol="IPv4",
        null=True,
        blank=True,
        help_text=_("Network containing the domain's IPv4 range (optional)."),
    )
    domaine_ip_netmask = models.IntegerField(
        default=24,
        validators=[MaxValueValidator(31), MinValueValidator(8)],
        help_text=_("Netmask for the domain's IPv4 range."),
    )
    reverse_v4 = models.BooleanField(
        default=False, help_text=_("Enable reverse DNS for IPv4.")
    )
    prefix_v6 = models.GenericIPAddressField(protocol="IPv6", null=True, blank=True)
    prefix_v6_length = models.IntegerField(
        default=64, validators=[MaxValueValidator(128), MinValueValidator(0)]
    )
    reverse_v6 = models.BooleanField(
        default=False, help_text=_("Enable reverse DNS for IPv6.")
    )
    vlan = models.ForeignKey("Vlan", on_delete=models.PROTECT, blank=True, null=True)
    ouverture_ports = models.ForeignKey("OuverturePortList", blank=True, null=True)

    class Meta:
        permissions = (
            ("view_iptype", _("Can view an IP type object")),
            ("use_all_iptype", _("Can use all IP types")),
        )
        verbose_name = _("IP type")
        verbose_name_plural = _("IP types")

    @cached_property
    def ip_range(self):
        """ Renvoie un objet IPRange à partir de l'objet IpType"""
        return IPRange(self.domaine_ip_start, end=self.domaine_ip_stop)

    @cached_property
    def ip_set(self):
        """ Renvoie une IPSet à partir de l'iptype"""
        return IPSet(self.ip_range)

    @cached_property
    def ip_set_as_str(self):
        """ Renvoie une liste des ip en string"""
        return [str(x) for x in self.ip_set]

    @cached_property
    def ip_set_cidrs_as_str(self):
        """Renvoie la liste des cidrs du range en str"""
        return [str(ip_range) for ip_range in self.ip_set.iter_cidrs()]

    @cached_property
    def ip_set_full_info(self):
        """Iter sur les range cidr, et renvoie network, broacast , etc"""
        return [
            {
                "network": str(ip_set.network),
                "netmask": str(ip_set.netmask),
                "netmask_cidr": str(ip_set.prefixlen),
                "broadcast": str(ip_set.broadcast),
                "vlan": str(self.vlan),
                "vlan_id": self.vlan.vlan_id,
            }
            for ip_set in self.ip_set.iter_cidrs()
        ]

    @cached_property
    def ip6_set_full_info(self):
        if self.prefix_v6:
            return {
                "network": str(self.prefix_v6),
                "netmask": "ffff:ffff:ffff:ffff::",
                "netmask_cidr": str(self.prefix_v6_length),
                "vlan": str(self.vlan),
                "vlan_id": self.vlan.vlan_id,
            }
        else:
            return None

    @cached_property
    def ip_network(self):
        """Renvoie le network parent du range start-stop, si spécifié
        Différent de ip_set_cidrs ou iP_set, car lui est supérieur ou égal"""
        if self.domaine_ip_network:
            return IPNetwork(
                str(self.domaine_ip_network) + "/" + str(self.domaine_ip_netmask)
            )
        return None

    @cached_property
    def ip_net_full_info(self):
        """Renvoie les infos du network contenant du range"""
        if self.ip_network:
            return {
                "network": str(self.ip_network.network),
                "netmask": str(self.ip_network.netmask),
                "broadcast": str(self.ip_network.broadcast),
                "netmask_cidr": str(self.ip_network.prefixlen),
                "vlan": str(self.vlan),
                "vlan_id": self.vlan.vlan_id,
            }
        else:
            return None

    @cached_property
    def complete_prefixv6(self):
        """Return the complete prefix v6 as cidr"""
        return str(self.prefix_v6) + "/" + str(self.prefix_v6_length)

    def ip_objects(self):
        """ Renvoie tous les objets ipv4 relié à ce type"""
        return IpList.objects.filter(ip_type=self)

    def free_ip(self):
        """ Renvoie toutes les ip libres associées au type donné (self)"""
        return IpList.objects.filter(interface__isnull=True).filter(ip_type=self)

    def gen_ip_range(self):
        """ Cree les IpList associées au type self. Parcours pédestrement et
        crée les ip une par une. Si elles existent déjà, met à jour le type
        associé à l'ip"""
        # Creation du range d'ip dans les objets iplist
        ip_obj = [IpList(ip_type=self, ipv4=str(ip)) for ip in self.ip_range]
        listes_ip = IpList.objects.filter(ipv4__in=[str(ip) for ip in self.ip_range])
        # Si il n'y a pas d'ip, on les crée
        if not listes_ip:
            IpList.objects.bulk_create(ip_obj)
        # Sinon on update l'ip_type
        else:
            listes_ip.update(ip_type=self)
        return

    def del_ip_range(self):
        """ Methode dépréciée, IpList est en mode cascade et supprimé
        automatiquement"""
        if Interface.objects.filter(ipv4__in=self.ip_objects()):
            raise ValidationError(
                _(
                    "One or several IP addresses from the"
                    " range are affected, impossible to delete"
                    " the range."
                )
            )
        for ip in self.ip_objects():
            ip.delete()

    def check_replace_prefixv6(self):
        """Remplace les prefixv6 des interfaces liées à ce type d'ip"""
        if not self.prefix_v6:
            return
        else:
            for ipv6 in Ipv6List.objects.filter(
                interface__in=Interface.objects.filter(
                    machine_type__in=MachineType.objects.filter(ip_type=self)
                )
            ):
                ipv6.check_and_replace_prefix(prefix=self.prefix_v6)

    def get_associated_ptr_records(self):
        from re2o.utils import all_active_assigned_interfaces

        if self.reverse_v4:
            return (
                all_active_assigned_interfaces()
                .filter(machine_type__ip_type=self)
                .filter(ipv4__isnull=False)
            )
        else:
            return None

    def get_associated_ptr_v6_records(self):
        from re2o.utils import all_active_interfaces

        if self.reverse_v6:
            return all_active_interfaces(full=True).filter(machine_type__ip_type=self)
        else:
            return None

    def clean(self):
        """ Nettoyage. Vérifie :
        - Que ip_stop est après ip_start
        - Qu'on ne crée pas plus gros qu'un /16
        - Que le range crée ne recoupe pas un range existant
        - Formate l'ipv6 donnée en /64"""
        if not self.domaine_ip_start or not self.domaine_ip_stop:
            raise ValidationError(_("Domaine IPv4 start and stop must be valid"))
        if IPAddress(self.domaine_ip_start) > IPAddress(self.domaine_ip_stop):
            raise ValidationError(_("Range end must be after range start..."))
        # On ne crée pas plus grand qu'un /16
        if self.ip_range.size > 65536:
            raise ValidationError(
                _(
                    "The range is too large, you can't create"
                    " a larger one than a /16."
                )
            )
        # On check que les / ne se recoupent pas
        for element in IpType.objects.all().exclude(pk=self.pk):
            if not self.ip_set.isdisjoint(element.ip_set):
                raise ValidationError(
                    _("The specified range is not disjoint from existing" " ranges.")
                )
        # On formate le prefix v6
        if self.prefix_v6:
            self.prefix_v6 = str(IPNetwork(self.prefix_v6 + "/64").network)
        # On vérifie qu'un domaine network/netmask contiens bien le domaine ip start-stop
        if self.domaine_ip_network:
            if (
                not self.domaine_ip_start in self.ip_network
                or not self.domaine_ip_stop in self.ip_network
            ):
                raise ValidationError(
                    _(
                        "If you specify a domain network or"
                        " netmask, it must contain the"
                        " domain's IP range."
                    )
                )
        return

    def save(self, *args, **kwargs):
        self.clean()
        super(IpType, self).save(*args, **kwargs)

    @staticmethod
    def can_use_all(user_request, *_args, **_kwargs):
        """Superdroit qui permet d'utiliser toutes les extensions sans
        restrictions
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return (
            user_request.has_perm("machines.use_all_iptype"),
            None,
            ("machines.use_all_iptype",),
        )

    def __str__(self):
        return self.name


class Vlan(RevMixin, AclMixin, models.Model):
    """ Un vlan : vlan_id et nom
    On limite le vlan id entre 0 et 4096, comme défini par la norme"""

    vlan_id = models.PositiveIntegerField(validators=[MaxValueValidator(4095)])
    name = models.CharField(max_length=256)
    comment = models.CharField(max_length=256, blank=True)
    # Réglages supplémentaires
    arp_protect = models.BooleanField(default=False)
    dhcp_snooping = models.BooleanField(default=False)
    dhcpv6_snooping = models.BooleanField(default=False)
    igmp = models.BooleanField(default=False, help_text=_("v4 multicast management."))
    mld = models.BooleanField(default=False, help_text=_("v6 multicast management."))

    class Meta:
        permissions = (("view_vlan", _("Can view a VLAN object")),)
        verbose_name = _("VLAN")
        verbose_name_plural = _("VLANs")

    def __str__(self):
        return self.name


class Nas(RevMixin, AclMixin, models.Model):
    """ Les nas. Associé à un machine_type.
    Permet aussi de régler le port_access_mode (802.1X ou mac-address) pour
    le radius. Champ autocapture de la mac à true ou false"""

    default_mode = "802.1X"
    AUTH = (("802.1X", "802.1X"), ("Mac-address", _("MAC-address")))

    name = models.CharField(max_length=255, unique=True)
    nas_type = models.ForeignKey(
        "MachineType", on_delete=models.PROTECT, related_name="nas_type"
    )
    machine_type = models.ForeignKey(
        "MachineType", on_delete=models.PROTECT, related_name="machinetype_on_nas"
    )
    port_access_mode = models.CharField(
        choices=AUTH, default=default_mode, max_length=32
    )
    autocapture_mac = models.BooleanField(default=False)

    class Meta:
        permissions = (("view_nas", _("Can view a NAS device object")),)
        verbose_name = _("NAS device")
        verbose_name_plural = _("NAS devices")

    def __str__(self):
        return self.name


class SOA(RevMixin, AclMixin, models.Model):
    """
    Un enregistrement SOA associé à une extension
    Les valeurs par défault viennent des recommandations RIPE :
    https://www.ripe.net/publications/docs/ripe-203
    """

    name = models.CharField(max_length=255)
    mail = models.EmailField(help_text=_("Contact email address for the zone."))
    refresh = models.PositiveIntegerField(
        default=86400,  # 24 hours
        help_text=_(
            "Seconds before the secondary DNS have to ask the primary"
            " DNS serial to detect a modification."
        ),
    )
    retry = models.PositiveIntegerField(
        default=7200,  # 2 hours
        help_text=_(
            "Seconds before the secondary DNS ask the serial again in"
            " case of a primary DNS timeout."
        ),
    )
    expire = models.PositiveIntegerField(
        default=3600000,  # 1000 hours
        help_text=_(
            "Seconds before the secondary DNS stop answering requests"
            " in case of primary DNS timeout."
        ),
    )
    ttl = models.PositiveIntegerField(
        default=172800, help_text=_("Time To Live.")  # 2 days
    )

    class Meta:
        permissions = (("view_soa", _("Can view an SOA record object")),)
        verbose_name = _("SOA record")
        verbose_name_plural = _("SOA records")

    def __str__(self):
        return str(self.name)

    @cached_property
    def dns_soa_param(self):
        """
        Renvoie la partie de l'enregistrement SOA correspondant aux champs :
            <refresh>   ; refresh
            <retry>     ; retry
            <expire>    ; expire
            <ttl>       ; TTL
        """
        return (
            "    {refresh}; refresh\n"
            "    {retry}; retry\n"
            "    {expire}; expire\n"
            "    {ttl}; TTL"
        ).format(
            refresh=str(self.refresh).ljust(12),
            retry=str(self.retry).ljust(12),
            expire=str(self.expire).ljust(12),
            ttl=str(self.ttl).ljust(12),
        )

    @cached_property
    def dns_soa_mail(self):
        """ Renvoie le mail dans l'enregistrement SOA """
        mail_fields = str(self.mail).split("@")
        return mail_fields[0].replace(".", "\\.") + "." + mail_fields[1] + "."

    @classmethod
    def new_default_soa(cls):
        """ Fonction pour créer un SOA par défaut, utile pour les nouvelles
        extensions .
        /!\ Ne jamais supprimer ou renommer cette fonction car elle est
        utilisée dans les migrations de la BDD. """
        return cls.objects.get_or_create(
            name=_("SOA to edit"), mail="postmaster@example.com"
        )[0].pk


class Extension(RevMixin, AclMixin, models.Model):
    """ Extension dns type example.org. Précise si tout le monde peut
    l'utiliser, associé à un origin (ip d'origine)"""

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Zone name, must begin with a dot (.example.org)."),
    )
    need_infra = models.BooleanField(default=False)
    origin = models.ForeignKey(
        "IpList",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=_("A record associated with the zone."),
    )
    origin_v6 = models.GenericIPAddressField(
        protocol="IPv6",
        null=True,
        blank=True,
        help_text=_("AAAA record associated with the zone."),
    )
    soa = models.ForeignKey("SOA", on_delete=models.CASCADE)
    dnssec = models.BooleanField(
        default=False, help_text=_("Should the zone be signed with DNSSEC.")
    )

    class Meta:
        permissions = (
            ("view_extension", _("Can view an extension object")),
            ("use_all_extension", _("Can use all extensions")),
        )
        verbose_name = _("DNS extension")
        verbose_name_plural = _("DNS extensions")

    @cached_property
    def dns_entry(self):
        """ Une entrée DNS A et AAAA sur origin (zone self)"""
        entry = ""
        if self.origin:
            entry += "@               IN  A       " + str(self.origin)
        if self.origin_v6:
            if entry:
                entry += "\n"
            entry += "@               IN  AAAA    " + str(self.origin_v6)
        return entry

    def get_associated_sshfp_records(self):
        from re2o.utils import all_active_assigned_interfaces

        return (
            all_active_assigned_interfaces()
            .filter(machine_type__ip_type__extension=self)
            .filter(machine__id__in=SshFp.objects.values("machine"))
        )

    def get_associated_a_records(self):
        from re2o.utils import all_active_assigned_interfaces

        return (
            all_active_assigned_interfaces()
            .filter(machine_type__ip_type__extension=self)
            .filter(ipv4__isnull=False)
        )

    def get_associated_aaaa_records(self):
        from re2o.utils import all_active_interfaces

        return all_active_interfaces(full=True).filter(
            machine_type__ip_type__extension=self
        )

    def get_associated_cname_records(self):
        from re2o.utils import all_active_assigned_interfaces

        return (
            Domain.objects.filter(extension=self)
            .filter(cname__interface_parent__in=all_active_assigned_interfaces())
            .prefetch_related("cname")
        )

    def get_associated_dname_records(self):
        return DName.objects.filter(alias=self)

    @staticmethod
    def can_use_all(user_request, *_args, **_kwargs):
        """Superdroit qui permet d'utiliser toutes les extensions sans
        restrictions
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        can = user_request.has_perm("machines.use_all_extension")
        return (
            can,
            _("You don't have the right to use all extensions.") if not can else None,
            ("machines.use_all_extension",),
        )

    def __str__(self):
        return self.name

    def clean(self, *args, **kwargs):
        if self.name and self.name[0] != ".":
            raise ValidationError(_("An extension must begin with a dot."))
        super(Extension, self).clean(*args, **kwargs)


class Mx(RevMixin, AclMixin, models.Model):
    """ Entrées des MX. Enregistre la zone (extension) associée et la
    priorité
    Todo : pouvoir associer un MX à une interface """

    zone = models.ForeignKey("Extension", on_delete=models.PROTECT)
    priority = models.PositiveIntegerField()
    name = models.ForeignKey("Domain", on_delete=models.PROTECT)
    ttl = models.PositiveIntegerField(
        verbose_name=_("Time To Live (TTL)"), default=172800  # 2 days
    )

    class Meta:
        permissions = (("view_mx", _("Can view an MX record object")),)
        verbose_name = _("MX record")
        verbose_name_plural = _("MX records")

    @cached_property
    def dns_entry(self):
        """Renvoie l'entrée DNS complète pour un MX à mettre dans les
        fichiers de zones"""
        return "@               IN  MX  {prior} {name}".format(
            prior=str(self.priority).ljust(3), name=str(self.name)
        )

    def __str__(self):
        return str(self.zone) + " " + str(self.priority) + " " + str(self.name)


class Ns(RevMixin, AclMixin, models.Model):
    """Liste des enregistrements name servers par zone considéérée"""

    zone = models.ForeignKey("Extension", on_delete=models.PROTECT)
    ns = models.ForeignKey("Domain", on_delete=models.PROTECT)
    ttl = models.PositiveIntegerField(
        verbose_name=_("Time To Live (TTL)"), default=172800  # 2 days
    )

    class Meta:
        permissions = (("view_ns", _("Can view an NS record object")),)
        verbose_name = _("NS record")
        verbose_name_plural = _("NS records")

    @cached_property
    def dns_entry(self):
        """Renvoie un enregistrement NS complet pour les filezones"""
        return "@               IN  NS      " + str(self.ns)

    def __str__(self):
        return str(self.zone) + " " + str(self.ns)


class Txt(RevMixin, AclMixin, models.Model):
    """ Un enregistrement TXT associé à une extension"""

    zone = models.ForeignKey("Extension", on_delete=models.PROTECT)
    field1 = models.CharField(max_length=255)
    field2 = models.TextField(max_length=2047)
    ttl = models.PositiveIntegerField(
        verbose_name=_("Time To Live (TTL)"), default=172800  # 2 days
    )

    class Meta:
        permissions = (("view_txt", _("Can view a TXT record object")),)
        verbose_name = _("TXT record")
        verbose_name_plural = _("TXT records")

    def __str__(self):
        return str(self.zone) + " : " + str(self.field1) + " " + str(self.field2)

    @cached_property
    def dns_entry(self):
        """Renvoie l'enregistrement TXT complet pour le fichier de zone"""
        return str(self.field1).ljust(15) + " IN  TXT     " + str(self.field2)


class DName(RevMixin, AclMixin, models.Model):
    """A DNAME entry for the DNS."""

    zone = models.ForeignKey("Extension", on_delete=models.PROTECT)
    alias = models.CharField(max_length=255)
    ttl = models.PositiveIntegerField(
        verbose_name=_("Time To Live (TTL)"), default=172800  # 2 days
    )

    class Meta:
        permissions = (("view_dname", _("Can view a DNAME record object")),)
        verbose_name = _("DNAME record")
        verbose_name_plural = _("DNAME records")

    def __str__(self):
        return str(self.zone) + " : " + str(self.alias)

    @cached_property
    def dns_entry(self):
        """Returns the DNAME record for the DNS zone file."""
        return str(self.alias).ljust(15) + " IN  DNAME   " + str(self.zone)


class Srv(RevMixin, AclMixin, models.Model):
    """ A SRV record """

    TCP = "TCP"
    UDP = "UDP"

    service = models.CharField(max_length=31)
    protocole = models.CharField(
        max_length=3, choices=((TCP, "TCP"), (UDP, "UDP")), default=TCP
    )
    extension = models.ForeignKey("Extension", on_delete=models.PROTECT)
    ttl = models.PositiveIntegerField(
        default=172800, help_text=_("Time To Live.")  # 2 days
    )
    priority = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(65535)],
        help_text=_(
            "Priority of the target server (positive integer value,"
            " the lower it is, the more the server will be used if"
            " available)."
        ),
    )
    weight = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(65535)],
        help_text=_(
            "Relative weight for records with the same priority"
            " (integer value between 0 and 65535)."
        ),
    )
    port = models.PositiveIntegerField(
        validators=[MaxValueValidator(65535)], help_text=_("TCP/UDP port.")
    )
    target = models.ForeignKey(
        "Domain", on_delete=models.PROTECT, help_text=_("Target server.")
    )

    class Meta:
        permissions = (("view_srv", _("Can view an SRV record object")),)
        verbose_name = _("SRV record")
        verbose_name_plural = _("SRV records")

    def __str__(self):
        return (
            str(self.service)
            + " "
            + str(self.protocole)
            + " "
            + str(self.extension)
            + " "
            + str(self.priority)
            + " "
            + str(self.weight)
            + str(self.port)
            + str(self.target)
        )

    @cached_property
    def dns_entry(self):
        """Renvoie l'enregistrement SRV complet pour le fichier de zone"""
        return (
            str(self.service)
            + "._"
            + str(self.protocole).lower()
            + str(self.extension)
            + ". "
            + str(self.ttl)
            + " IN SRV "
            + str(self.priority)
            + " "
            + str(self.weight)
            + " "
            + str(self.port)
            + " "
            + str(self.target)
            + "."
        )


class SshFp(RevMixin, AclMixin, models.Model):
    """A fingerprint of an SSH public key"""

    ALGO = (
        ("ssh-rsa", "ssh-rsa"),
        ("ssh-ed25519", "ssh-ed25519"),
        ("ecdsa-sha2-nistp256", "ecdsa-sha2-nistp256"),
        ("ecdsa-sha2-nistp384", "ecdsa-sha2-nistp384"),
        ("ecdsa-sha2-nistp521", "ecdsa-sha2-nistp521"),
    )

    machine = models.ForeignKey("Machine", on_delete=models.CASCADE)
    pub_key_entry = models.TextField(help_text=_("SSH public key."), max_length=2048)
    algo = models.CharField(choices=ALGO, max_length=32)
    comment = models.CharField(
        help_text=_("Comment."), max_length=255, null=True, blank=True
    )

    @cached_property
    def algo_id(self):
        """Return the id of the algorithm for this key"""
        if "ecdsa" in self.algo:
            return 3
        elif "rsa" in self.algo:
            return 1
        else:
            return 2

    @cached_property
    def hash(self):
        """Return the hashess for the pub key with correct id
        cf RFC, 1 is sha1 , 2 sha256"""
        return {
            "1": hashlib.sha1(base64.b64decode(self.pub_key_entry)).hexdigest(),
            "2": hashlib.sha256(base64.b64decode(self.pub_key_entry)).hexdigest(),
        }

    class Meta:
        permissions = (("view_sshfp", _("Can view an SSHFP record object")),)
        verbose_name = _("SSHFP record")
        verbose_name_plural = _("SSHFP records")

    def can_view(self, user_request, *_args, **_kwargs):
        return self.machine.can_view(user_request, *_args, **_kwargs)

    def can_edit(self, user_request, *args, **kwargs):
        return self.machine.can_edit(user_request, *args, **kwargs)

    def can_delete(self, user_request, *args, **kwargs):
        return self.machine.can_delete(user_request, *args, **kwargs)

    def __str__(self):
        return str(self.algo) + " " + str(self.comment)


class Interface(RevMixin, AclMixin, FieldPermissionModelMixin, models.Model):
    """ Une interface. Objet clef de l'application machine :
    - une address mac unique. Possibilité de la rendre unique avec le
    typemachine
    - une onetoone vers IpList pour attribution ipv4
    - le type parent associé au range ip et à l'extension
    - un objet domain associé contenant son nom
    - la liste des ports oiuvert"""

    ipv4 = models.OneToOneField(
        "IpList", on_delete=models.PROTECT, blank=True, null=True
    )
    mac_address = MACAddressField(integer=False)
    machine = models.ForeignKey("Machine", on_delete=models.CASCADE)
    machine_type = models.ForeignKey("MachineType", on_delete=models.PROTECT)
    details = models.CharField(max_length=255, blank=True)
    port_lists = models.ManyToManyField("OuverturePortList", blank=True)

    class Meta:
        permissions = (
            ("view_interface", _("Can view an interface object")),
            ("change_interface_machine", _("Can change the owner of an interface")),
        )
        verbose_name = _("interface")
        verbose_name_plural = _("interfaces")

    @cached_property
    def is_active(self):
        """ Renvoie si une interface doit avoir accès ou non """
        machine = self.machine
        user = self.machine.user
        return machine.active and user.has_access()

    @cached_property
    def ipv6_slaac(self):
        """ Renvoie un objet type ipv6 à partir du prefix associé à
        l'iptype parent"""
        if self.machine_type.ip_type.prefix_v6:
            return EUI(self.mac_address).ipv6(
                IPNetwork(self.machine_type.ip_type.prefix_v6).network
            )
        else:
            return None

    @cached_property
    def gen_ipv6_dhcpv6(self):
        """Cree une ip, à assigner avec dhcpv6 sur une machine"""
        prefix_v6 = self.machine_type.ip_type.prefix_v6.encode().decode("utf-8")
        if not prefix_v6:
            return None
        return IPv6Address(
            IPv6Address(prefix_v6).exploded[:20] + IPv6Address(self.id).exploded[20:]
        )

    @cached_property
    def get_vendor(self):
        """Retourne le vendeur associé à la mac de l'interface"""
        mac = EUI(self.mac_address)
        try:
            oui = mac.oui
            vendor = oui.registration().org
        except (IndexError, NotRegisteredError) as error:
            vendor = _("Unknown vendor.")
        return vendor

    def sync_ipv6_dhcpv6(self):
        """Affecte une ipv6 dhcpv6 calculée à partir de l'id de la machine"""
        ipv6_dhcpv6 = self.gen_ipv6_dhcpv6
        if not ipv6_dhcpv6:
            return
        ipv6 = Ipv6List.objects.filter(ipv6=str(ipv6_dhcpv6)).first()
        if not ipv6:
            ipv6 = Ipv6List(ipv6=str(ipv6_dhcpv6))
        ipv6.interface = self
        ipv6.save()
        return

    def sync_ipv6_slaac(self):
        """Cree, mets à jour et supprime si il y a lieu l'ipv6 slaac associée
        à la machine
        Sans prefixe ipv6, on return
        Si l'ip slaac n'est pas celle qu'elle devrait être, on maj"""
        ipv6_slaac = self.ipv6_slaac
        if not ipv6_slaac:
            return
        ipv6_object = Ipv6List.objects.filter(interface=self, slaac_ip=True).first()
        if not ipv6_object:
            ipv6_object = Ipv6List(interface=self, slaac_ip=True)
        if ipv6_object.ipv6 != str(ipv6_slaac):
            ipv6_object.ipv6 = str(ipv6_slaac)
            ipv6_object.save()

    def sync_ipv6(self):
        """Cree et met à jour l'ensemble des ipv6 en fonction du mode choisi"""
        if preferences.models.OptionalMachine.get_cached_value("ipv6_mode") == "SLAAC":
            self.sync_ipv6_slaac()
        elif (
            preferences.models.OptionalMachine.get_cached_value("ipv6_mode") == "DHCPV6"
        ):
            self.sync_ipv6_dhcpv6()
        else:
            return

    def ipv6(self):
        """ Renvoie le queryset de la liste des ipv6
        On renvoie l'ipv6 slaac que si le mode slaac est activé
        (et non dhcpv6)"""
        if preferences.models.OptionalMachine.get_cached_value("ipv6_mode") == "SLAAC":
            return self.ipv6list.all()
        elif (
            preferences.models.OptionalMachine.get_cached_value("ipv6_mode") == "DHCPV6"
        ):
            return self.ipv6list.filter(slaac_ip=False)
        else:
            return []

    def mac_bare(self):
        """ Formatage de la mac type mac_bare"""
        return str(EUI(self.mac_address, dialect=mac_bare)).lower()

    def filter_macaddress(self):
        """ Tente un formatage mac_bare, si échoue, lève une erreur de
        validation"""
        try:
            self.mac_address = str(EUI(self.mac_address, dialect=default_dialect()))
        except:
            raise ValidationError(_("The given MAC address is invalid."))

    def assign_ipv4(self):
        """ Assigne une ip à l'interface """
        free_ips = self.machine_type.ip_type.free_ip()
        if free_ips:
            self.ipv4 = free_ips[0]
        else:
            raise ValidationError(
                _("There are no IP addresses available in the slash.")
            )
        return

    def unassign_ipv4(self):
        """ Sans commentaire, désassigne une ipv4"""
        self.ipv4 = None

    @classmethod
    def mass_unassign_ipv4(cls, interface_list):
        """Unassign ipv4 to multiple interfaces"""
        with transaction.atomic(), reversion.create_revision():
            interface_list.update(ipv4=None)
            reversion.set_comment("IPv4 unassignment")

    @classmethod
    def mass_assign_ipv4(cls, interface_list):
        for interface in interface_list:
            with transaction.atomic(), reversion.create_revision():
                interface.assign_ipv4()
                interface.save()
                reversion.set_comment("IPv4 assignment")

    def update_type(self):
        """ Lorsque le machinetype est changé de type d'ip, on réassigne"""
        self.clean()
        self.save()

    def has_private_ip(self):
        """ True si l'ip associée est privée"""
        if self.ipv4:
            return IPAddress(str(self.ipv4)).is_private()
        else:
            return False

    def may_have_port_open(self):
        """ True si l'interface a une ip et une ip publique.
        Permet de ne pas exporter des ouvertures sur des ip privées
        (useless)"""
        return self.ipv4 and not self.has_private_ip()

    def clean(self, *args, **kwargs):
        """ Formate l'addresse mac en mac_bare (fonction filter_mac)
        et assigne une ipv4 dans le bon range si inexistante ou incohérente"""
        # If type was an invalid value, django won't create an attribute type
        # but try clean() as we may be able to create it from another value
        # so even if the error as yet been detected at this point, django
        # continues because the error might not prevent us from creating the
        # instance.
        # But in our case, it's impossible to create a type value so we raise
        # the error.
        if not hasattr(self, "machine_type"):
            raise ValidationError(_("The selected IP type is invalid."))
        self.filter_macaddress()
        if not self.ipv4 or self.machine_type.ip_type != self.ipv4.ip_type:
            self.assign_ipv4()
        super(Interface, self).clean(*args, **kwargs)

    def validate_unique(self, *args, **kwargs):
        super(Interface, self).validate_unique(*args, **kwargs)
        interfaces_similar = Interface.objects.filter(
            mac_address=self.mac_address,
            machine_type__ip_type=self.machine_type.ip_type,
        )
        if interfaces_similar and interfaces_similar.first() != self:
            raise ValidationError(
                _("MAC address already registered in this machine type/subnet.")
            )

    def save(self, *args, **kwargs):
        self.filter_macaddress()
        # On verifie la cohérence en forçant l'extension par la méthode
        if self.ipv4:
            if self.machine_type.ip_type != self.ipv4.ip_type:
                raise ValidationError(
                    _("The IPv4 address and the machine type don't match.")
                )
        self.validate_unique()
        super(Interface, self).save(*args, **kwargs)

    @staticmethod
    def can_create(user_request, machineid, *_args, **_kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        une interface, ou bien que la machine appartient bien à l'user
        :param macineid: Id de la machine parente de l'interface
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        try:
            machine = Machine.objects.get(pk=machineid)
        except Machine.DoesNotExist:
            return False, _("Nonexistent machine."), None
        if not user_request.has_perm("machines.add_interface"):
            if not (
                preferences.models.OptionalMachine.get_cached_value("create_machine")
            ):
                return (
                    False,
                    _("You don't have the right to add a machine."),
                    ("machines.add_interface",),
                )
            max_lambdauser_interfaces = preferences.models.OptionalMachine.get_cached_value(
                "max_lambdauser_interfaces"
            )
            if machine.user != user_request:
                return (
                    False,
                    _(
                        "You don't have the right to add an interface"
                        " to a machine of another user."
                    ),
                    ("machines.add_interface",),
                )
            if machine.user.user_interfaces().count() >= max_lambdauser_interfaces:
                return (
                    False,
                    _(
                        "You reached the maximum number of interfaces"
                        " that you are allowed to create yourself"
                        " (%s)." % max_lambdauser_interfaces
                    ),
                    ("machines.add_interface",),
                )
        return True, None, None

    @staticmethod
    def can_change_machine(user_request, *_args, **_kwargs):
        """Check if a user can change the machine associated with an
        Interface object """
        can = user_request.has_perm("machines.change_interface_machine")
        return (
            can,
            _("You don't have the right to edit the machine.") if not can else None,
            ("machines.change_interface_machine",),
        )

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance interface, ou qu'elle lui appartient
        :param self: Instance interface à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if self.machine.user != user_request:
            can_user, _message, permissions = self.machine.user.can_edit(
                user_request, *args, **kwargs
            )
            if not (user_request.has_perm("machines.change_interface") and can_user):
                return (
                    False,
                    _("You don't have the right to edit a machine of another" " user."),
                    ("machines.change_interface",) + (permissions or ()),
                )
        return True, None, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits delete object pour del
        cette instance interface, ou qu'elle lui appartient
        :param self: Instance interface à del
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if self.machine.user != user_request:
            can_user, _message, permissions = self.machine.user.can_edit(
                user_request, *args, **kwargs
            )
            if not (user_request.has_perm("machines.delete_interface") and can_user):
                return (
                    False,
                    _(
                        "You don't have the right to delete interfaces of another"
                        " user."
                    ),
                    ("machines.delete_interface",) + (permissions or ()),
                )
        return True, None, None

    def can_view(self, user_request, *_args, **_kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet ou qu'elle appartient à l'user
        :param self: instance interface à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if (
            not user_request.has_perm("machines.view_interface")
            and self.machine.user != user_request
        ):
            return (
                False,
                _("You don't have the right to view interfaces other than yours."),
                ("machines.view_interface",),
            )
        return True, None, None

    def __init__(self, *args, **kwargs):
        super(Interface, self).__init__(*args, **kwargs)
        self.field_permissions = {"machine": self.can_change_machine}

    def __str__(self):
        try:
            domain = self.domain
        except:
            domain = None
        return str(domain)


class Ipv6List(RevMixin, AclMixin, FieldPermissionModelMixin, models.Model):
    """ A list of IPv6 """

    ipv6 = models.GenericIPAddressField(protocol="IPv6")
    interface = models.ForeignKey(
        "Interface", on_delete=models.CASCADE, related_name="ipv6list"
    )
    slaac_ip = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("view_ipv6list", _("Can view an IPv6 addresses list object")),
            (
                "change_ipv6list_slaac_ip",
                _("Can change the SLAAC value of an IPv6 addresses list"),
            ),
        )
        verbose_name = _("IPv6 addresses list")
        verbose_name_plural = _("IPv6 addresses lists")

    @staticmethod
    def can_create(user_request, interfaceid, *_args, **_kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        une ipv6, ou possède l'interface associée
        :param interfaceid: Id de l'interface associée à cet objet domain
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        try:
            interface = Interface.objects.get(pk=interfaceid)
        except Interface.DoesNotExist:
            return False, _("Nonexistent interface."), None
        if not user_request.has_perm("machines.add_ipv6list"):
            if interface.machine.user != user_request:
                return (
                    False,
                    _(
                        "You don't have the right to add ipv6 to a"
                        " machine of another user."
                    ),
                    ("machines.add_ipv6list",),
                )
        return True, None, None

    @staticmethod
    def can_change_slaac_ip(user_request, *_args, **_kwargs):
        """ Check if a user can change the slaac value """
        can = user_request.has_perm("machines.change_ipv6list_slaac_ip")
        return (
            can,
            _("You don't have the right to change the SLAAC value of an IPv6 address.")
            if not can
            else None,
            ("machines.change_ipv6list_slaac_ip",),
        )

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance interface, ou qu'elle lui appartient
        :param self: Instance interface à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if self.interface.machine.user != user_request:
            can_user, _message, permissions = self.interface.machine.user.can_edit(
                user_request, *args, **kwargs
            )
            if not (user_request.has_perm("machines.change_ipv6list") and can_user):
                return (
                    False,
                    _(
                        "You don't have the right to edit ipv6 of a machine of another user."
                    ),
                    ("machines.change_ipv6list",),
                )
        return True, None, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits delete object pour del
        cette instance interface, ou qu'elle lui appartient
        :param self: Instance interface à del
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if self.interface.machine.user != user_request:
            can_user, _message, permissions = self.interface.machine.user.can_edit(
                user_request, *args, **kwargs
            )
            if not (user_request.has_perm("machines.delete_ipv6list") and can_user):
                return (
                    False,
                    _(
                        "You don't have the right to delete ipv6 of a machine of another user."
                    ),
                    ("machines.delete_ipv6list",) + (permissions or ()),
                )
        return True, None, None

    def can_view(self, user_request, *_args, **_kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet ou qu'elle appartient à l'user
        :param self: instance interface à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if (
            not user_request.has_perm("machines.view_ipv6list")
            and self.interface.machine.user != user_request
        ):
            return (
                False,
                _(
                    "You don't have the right to view ipv6 of machines other than yours."
                ),
                ("machines.view_ipv6list",),
            )
        return True, None, None

    def __init__(self, *args, **kwargs):
        super(Ipv6List, self).__init__(*args, **kwargs)
        self.field_permissions = {"slaac_ip": self.can_change_slaac_ip}

    def check_and_replace_prefix(self, prefix=None):
        """Si le prefixe v6 est incorrect, on maj l'ipv6"""
        prefix_v6 = prefix or self.interface.machine_type.ip_type.prefix_v6.encode().decode(
            "utf-8"
        )
        if not prefix_v6:
            return
        if (
            IPv6Address(self.ipv6.encode().decode("utf-8")).exploded[:20]
            != IPv6Address(prefix_v6).exploded[:20]
        ):
            self.ipv6 = IPv6Address(
                IPv6Address(prefix_v6).exploded[:20]
                + IPv6Address(self.ipv6.encode().decode("utf-8")).exploded[20:]
            )
            self.save()

    def clean(self, *args, **kwargs):
        if self.slaac_ip and (
            Ipv6List.objects.filter(interface=self.interface, slaac_ip=True).exclude(
                id=self.id
            )
        ):
            raise ValidationError(_("A SLAAC IP address is already registered."))
        try:
            prefix_v6 = self.interface.machine_type.ip_type.prefix_v6.encode().decode(
                "utf-8"
            )
        except AttributeError:  # Prevents from crashing when there is no defined prefix_v6
            prefix_v6 = None
        if prefix_v6:
            if (
                IPv6Address(self.ipv6.encode().decode("utf-8")).exploded[:20]
                != IPv6Address(prefix_v6).exploded[:20]
            ):
                raise ValidationError(
                    _(
                        "The v6 prefix is incorrect and"
                        " doesn't match the type associated"
                        " with the machine."
                    )
                )
        super(Ipv6List, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Force à avoir appellé clean avant"""
        self.full_clean()
        super(Ipv6List, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.ipv6)


class Domain(RevMixin, AclMixin, FieldPermissionModelMixin, models.Model):
    """ Objet domain. Enregistrement A et CNAME en même temps : permet de
    stocker les alias et les nom de machines, suivant si interface_parent
    ou cname sont remplis"""

    interface_parent = models.OneToOneField(
        "Interface", on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(
        help_text=_("Mandatory and unique, must not contain dots."), max_length=255
    )
    extension = models.ForeignKey("Extension", on_delete=models.PROTECT)
    cname = models.ForeignKey(
        "self", null=True, blank=True, related_name="related_domain"
    )
    ttl = models.PositiveIntegerField(
        verbose_name=_("Time To Live (TTL)"),
        default=0  # 0 means that the re2o-service for DNS should retrieve the
        # default TTL
    )

    class Meta:
        unique_together = (("name", "extension"),)
        permissions = (
            ("view_domain", _("Can view a domain object")),
            ("change_ttl", _("Can change the TTL of a domain object")),
        )
        verbose_name = _("domain")
        verbose_name_plural = _("domains")

    def get_extension(self):
        """ Retourne l'extension de l'interface parente si c'est un A
         Retourne l'extension propre si c'est un cname, renvoie None sinon"""
        if self.interface_parent:
            return self.interface_parent.machine_type.ip_type.extension
        elif hasattr(self, "extension"):
            return self.extension
        else:
            return None

    def clean(self):
        """ Validation :
        - l'objet est bien soit A soit CNAME
        - le cname est pas pointé sur lui-même
        - le nom contient bien les caractères autorisés par la norme
        dns et moins de 63 caractères au total
        - le couple nom/extension est bien unique"""
        if self.get_extension():
            self.extension = self.get_extension()
        if self.interface_parent and self.cname:
            raise ValidationError(_("You can't create a both A and CNAME record."))
        if self.cname == self:
            raise ValidationError(
                _("You can't create a CNAME record pointing to itself.")
            )
        HOSTNAME_LABEL_PATTERN = re.compile(r"(?!-)[a-z\d-]+(?<!-)$")
        self.name = self.name.lower()
        if len(self.name) > 63:
            raise ValidationError(
                _("The domain name %s is too long (over 63 characters).") % self.name
            )
        if not HOSTNAME_LABEL_PATTERN.match(self.name):
            raise ValidationError(
                _("The domain name %s contains forbidden characters.") % self.name
            )
        self.validate_unique()
        super(Domain, self).clean()

    @cached_property
    def dns_entry(self):
        """ Une entrée DNS"""
        if self.cname:
            return "{name} IN CNAME   {cname}.".format(
                name=str(self.name).ljust(15), cname=str(self.cname)
            )

    def save(self, *args, **kwargs):
        """ Empèche le save sans extension valide.
        Force à avoir appellé clean avant"""
        if not self.get_extension():
            raise ValidationError(_("Invalid extension."))
        self.full_clean()
        super(Domain, self).save(*args, **kwargs)

    @cached_property
    def get_source_interface(self):
        """Renvoie l'interface source :
        - l'interface reliée si c'est un A
        - si c'est un cname, suit le cname jusqu'à atteindre le A
        et renvoie l'interface parente
        Fonction récursive"""
        if self.interface_parent:
            return self.interface_parent
        else:
            return self.cname.get_source_interface

    @staticmethod
    def can_create(user_request, interfaceid, *_args, **_kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un domain, ou possède l'interface associée
        :param interfaceid: Id de l'interface associée à cet objet domain
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        try:
            interface = Interface.objects.get(pk=interfaceid)
        except Interface.DoesNotExist:
            return False, _("Nonexistent interface."), None
        if not user_request.has_perm("machines.add_domain"):
            max_lambdauser_aliases = preferences.models.OptionalMachine.get_cached_value(
                "max_lambdauser_aliases"
            )
            if interface.machine.user != user_request:
                return (
                    False,
                    _(
                        "You don't have the right to add an alias to a"
                        " machine of another user."
                    ),
                    ("machines.add_domain",),
                )
            if (
                Domain.objects.filter(
                    cname__in=Domain.objects.filter(
                        interface_parent__in=(interface.machine.user.user_interfaces())
                    )
                ).count()
                >= max_lambdauser_aliases
            ):
                return (
                    False,
                    _(
                        "You reached the maximum number of alias that"
                        " you are allowed to create yourself (%s). "
                        % max_lambdauser_aliases
                    ),
                    ("machines.add_domain",),
                )
        return True, None, None

    def can_edit(self, user_request, *_args, **_kwargs):
        """Verifie que l'user a les bons droits pour editer
        cette instance domain
        :param self: Instance domain à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if (
            not user_request.has_perm("machines.change_domain")
            and self.get_source_interface.machine.user != user_request
        ):
            return (
                False,
                _(
                    "You don't have the right to edit an alias of a"
                    " machine of another user."
                ),
                ("machines.change_domain",),
            )
        return True, None, None

    def can_delete(self, user_request, *_args, **_kwargs):
        """Verifie que l'user a les bons droits delete object pour del
        cette instance domain, ou qu'elle lui appartient
        :param self: Instance domain à del
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if (
            not user_request.has_perm("machines.delete_domain")
            and self.get_source_interface.machine.user != user_request
        ):
            return (
                False,
                _(
                    "You don't have the right to delete an alias of a"
                    " machine of another user."
                ),
                ("machines.delete_domain",),
            )
        return True, None, None

    def can_view(self, user_request, *_args, **_kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet ou qu'elle appartient à l'user
        :param self: instance domain à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if (
            not user_request.has_perm("machines.view_domain")
            and self.get_source_interface.machine.user != user_request
        ):
            return (
                False,
                _("You don't have the right to view other machines than" " yours."),
                ("machines.view_domain",),
            )
        return True, None, None

    @staticmethod
    def can_change_ttl(user_request, *_args, **_kwargs):
        can = user_request.has_perm("machines.change_ttl")
        return (
            can,
            _("You don't have the right to change the domain's TTL.")
            if not can
            else None,
            ("machines.change_ttl",),
        )

    def __str__(self):
        return str(self.name) + str(self.extension)


class IpList(RevMixin, AclMixin, models.Model):
    """ A list of IPv4 """

    ipv4 = models.GenericIPAddressField(protocol="IPv4", unique=True)
    ip_type = models.ForeignKey("IpType", on_delete=models.CASCADE)

    class Meta:
        permissions = (("view_iplist", _("Can view an IPv4 addresses list object")),)
        verbose_name = _("IPv4 addresses list")
        verbose_name_plural = _("IPv4 addresses lists")

    @cached_property
    def need_infra(self):
        """ Permet de savoir si un user basique peut assigner cette ip ou
        non"""
        return self.ip_type.need_infra

    def clean(self):
        """ Erreur si l'ip_type est incorrect"""
        if not str(self.ipv4) in self.ip_type.ip_set_as_str:
            raise ValidationError(
                _("The IPv4 address and the range of the IP type don't match.")
            )
        return

    def save(self, *args, **kwargs):
        self.clean()
        super(IpList, self).save(*args, **kwargs)

    def __str__(self):
        return self.ipv4


class Role(RevMixin, AclMixin, models.Model):
    """Define the role of a machine.
    Allow automated generation of the server configuration.
    """

    ROLE = (
        ("dhcp-server", _("DHCP server")),
        ("switch-conf-server", _("Switches configuration server")),
        ("dns-recursive-server", _("Recursive DNS server")),
        ("ntp-server", _("NTP server")),
        ("radius-server", _("RADIUS server")),
        ("log-server", _("Log server")),
        ("ldap-master-server", _("LDAP master server")),
        ("ldap-backup-server", _("LDAP backup server")),
        ("smtp-server", _("SMTP server")),
        ("postgresql-server", _("postgreSQL server")),
        ("mysql-server", _("mySQL server")),
        ("sql-client", _("SQL client")),
        ("gateway", _("Gateway")),
    )

    role_type = models.CharField(max_length=255, unique=True)
    servers = models.ManyToManyField("Interface")
    specific_role = models.CharField(choices=ROLE, null=True, blank=True, max_length=32)

    class Meta:
        permissions = (("view_role", _("Can view a role object")),)
        verbose_name = _("server role")
        verbose_name_plural = _("server roles")

    @classmethod
    def interface_for_roletype(cls, roletype):
        """Return interfaces for a roletype"""
        return Interface.objects.filter(role=cls.objects.filter(specific_role=roletype))

    @classmethod
    def all_interfaces_for_roletype(cls, roletype):
        """Return all interfaces for a roletype"""
        return Interface.objects.filter(
            machine__interface__role=cls.objects.filter(specific_role=roletype)
        )

    @classmethod
    def interface_for_roletype(cls, roletype):
        """Return interfaces for a roletype"""
        return Interface.objects.filter(role=cls.objects.filter(specific_role=roletype))

    def save(self, *args, **kwargs):
        super(Role, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.role_type)


class Service(RevMixin, AclMixin, models.Model):
    """ Definition d'un service (dhcp, dns, etc)"""

    service_type = models.CharField(max_length=255, blank=True, unique=True)
    min_time_regen = models.DurationField(
        default=timedelta(minutes=1),
        help_text=_("Minimal time before regeneration of the service."),
    )
    regular_time_regen = models.DurationField(
        default=timedelta(hours=1),
        help_text=_("Maximal time before regeneration of the service."),
    )
    servers = models.ManyToManyField("Interface", through="Service_link")

    class Meta:
        permissions = (("view_service", _("Can view a service object")),)
        verbose_name = _("service to generate (DHCP, DNS, ...)")
        verbose_name_plural = _("services to generate (DHCP, DNS, ...)")

    def ask_regen(self):
        """ Marque à True la demande de régénération pour un service x """
        Service_link.objects.filter(service=self).exclude(asked_regen=True).update(
            asked_regen=True
        )
        return

    def process_link(self, servers):
        """ Django ne peut créer lui meme les relations manytomany avec table
        intermediaire explicite"""
        for serv in servers.exclude(pk__in=Interface.objects.filter(service=self)):
            link = Service_link(service=self, server=serv)
            link.save()
        Service_link.objects.filter(service=self).exclude(server__in=servers).delete()
        return

    def save(self, *args, **kwargs):
        super(Service, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.service_type)


def regen(service):
    """ Fonction externe pour régérération d'un service, prend un objet service
    en arg"""
    obj = Service.objects.filter(service_type=service)
    if obj:
        obj[0].ask_regen()
    return


class Service_link(RevMixin, AclMixin, models.Model):
    """ Definition du lien entre serveurs et services"""

    service = models.ForeignKey("Service", on_delete=models.CASCADE)
    server = models.ForeignKey("Interface", on_delete=models.CASCADE)
    last_regen = models.DateTimeField(auto_now_add=True)
    asked_regen = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("view_service_link", _("Can view a service server link object")),
        )
        verbose_name = _("link between service and server")
        verbose_name_plural = _("links between service and server")

    def done_regen(self):
        """ Appellé lorsqu'un serveur a regénéré son service"""
        self.last_regen = timezone.now()
        self.asked_regen = False
        self.save()

    @property
    def need_regen(self):
        """ Décide si le temps minimal écoulé est suffisant pour provoquer une
        régénération de service"""
        return bool(
            (
                self.asked_regen
                and (self.last_regen + self.service.min_time_regen) < timezone.now()
            )
            or (self.last_regen + self.service.regular_time_regen) < timezone.now()
        )

    @need_regen.setter
    def need_regen(self, value):
        """
        Force to set the need_regen value. True means a regen is asked and False
        means a regen has been done.

        :param value: (bool) The value to set to
        """
        if not value:
            self.last_regen = timezone.now()
        self.asked_regen = value
        self.save()

    def __str__(self):
        return str(self.server) + " " + str(self.service)


class OuverturePortList(RevMixin, AclMixin, models.Model):
    """Liste des ports ouverts sur une interface."""

    name = models.CharField(
        help_text=_("Name of the ports configuration"), max_length=255
    )

    class Meta:
        permissions = (
            ("view_ouvertureportlist", _("Can view a ports opening list" " object")),
        )
        verbose_name = _("ports opening list")
        verbose_name_plural = _("ports opening lists")

    def can_delete(self, user_request, *_args, **_kwargs):
        """Verifie que l'user a les bons droits bureau pour delete
        cette instance ouvertureportlist
        :param self: Instance ouvertureportlist à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm("machines.delete_ouvertureportlist"):
            return (
                False,
                _("You don't have the right to delete a ports opening list."),
                ("machines.delete_ouvertureportlist",),
            )
        if self.interface_set.all():
            return False, _("This ports opening list is used."), None
        return True, None, None

    def __str__(self):
        return self.name

    def tcp_ports_in(self):
        """Renvoie la liste des ports ouverts en TCP IN pour ce profil"""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.TCP, io=OuverturePort.IN
        )

    def udp_ports_in(self):
        """Renvoie la liste des ports ouverts en UDP IN pour ce profil"""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.UDP, io=OuverturePort.IN
        )

    def tcp_ports_out(self):
        """Renvoie la liste des ports ouverts en TCP OUT pour ce profil"""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.TCP, io=OuverturePort.OUT
        )

    def udp_ports_out(self):
        """Renvoie la liste des ports ouverts en UDP OUT pour ce profil"""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.UDP, io=OuverturePort.OUT
        )


class OuverturePort(RevMixin, AclMixin, models.Model):
    """
    Représente un simple port ou une plage de ports.

    Les ports de la plage sont compris entre begin et en inclus.
    Si begin == end alors on ne représente qu'un seul port.

    On limite les ports entre 0 et 65535, tels que défini par la RFC
    """

    TCP = "T"
    UDP = "U"
    IN = "I"
    OUT = "O"
    begin = models.PositiveIntegerField(validators=[MaxValueValidator(65535)])
    end = models.PositiveIntegerField(validators=[MaxValueValidator(65535)])
    port_list = models.ForeignKey("OuverturePortList", on_delete=models.CASCADE)
    protocole = models.CharField(
        max_length=1, choices=((TCP, "TCP"), (UDP, "UDP")), default=TCP
    )
    io = models.CharField(max_length=1, choices=((IN, "IN"), (OUT, "OUT")), default=OUT)

    class Meta:
        verbose_name = _("ports opening")
        verbose_name_plural = _("ports openings")

    def __str__(self):
        if self.begin == self.end:
            return str(self.begin)
        return ":".join([str(self.begin), str(self.end)])

    def show_port(self):
        """Formatage plus joli, alias pour str"""
        return str(self)


@receiver(post_save, sender=Machine)
def machine_post_save(**kwargs):
    """Synchronisation ldap et régen parefeu/dhcp lors de la modification
    d'une machine"""
    user = kwargs["instance"].user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)
    regen("dhcp")
    regen("mac_ip_list")


@receiver(post_delete, sender=Machine)
def machine_post_delete(**kwargs):
    """Synchronisation ldap et régen parefeu/dhcp lors de la suppression
    d'une machine"""
    machine = kwargs["instance"]
    user = machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)
    regen("dhcp")
    regen("mac_ip_list")


@receiver(post_save, sender=Interface)
def interface_post_save(**kwargs):
    """Synchronisation ldap et régen parefeu/dhcp lors de la modification
    d'une interface"""
    interface = kwargs["instance"]
    interface.sync_ipv6()
    user = interface.machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)
    # Regen services
    regen("dhcp")
    regen("mac_ip_list")


@receiver(post_delete, sender=Interface)
def interface_post_delete(**kwargs):
    """Synchronisation ldap et régen parefeu/dhcp lors de la suppression
    d'une interface"""
    interface = kwargs["instance"]
    user = interface.machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)


@receiver(post_save, sender=IpType)
def iptype_post_save(**kwargs):
    """Generation des objets ip après modification d'un range ip"""
    iptype = kwargs["instance"]
    iptype.gen_ip_range()
    iptype.check_replace_prefixv6()


@receiver(post_save, sender=MachineType)
def machinetype_post_save(**kwargs):
    """Mise à jour des interfaces lorsque changement d'attribution
    d'une machinetype (changement iptype parent)"""
    machinetype = kwargs["instance"]
    for interface in machinetype.all_interfaces():
        interface.update_type()


@receiver(post_save, sender=Domain)
def domain_post_save(**_kwargs):
    """Regeneration dns après modification d'un domain object"""
    regen("dns")


@receiver(post_delete, sender=Domain)
def domain_post_delete(**_kwargs):
    """Regeneration dns après suppression d'un domain object"""
    regen("dns")


@receiver(post_save, sender=Extension)
def extension_post_save(**_kwargs):
    """Regeneration dns après modification d'une extension"""
    regen("dns")


@receiver(post_delete, sender=Extension)
def extension_post_delete(**_kwargs):
    """Regeneration dns après suppression d'une extension"""
    regen("dns")


@receiver(post_save, sender=SOA)
def soa_post_save(**_kwargs):
    """Regeneration dns après modification d'un SOA"""
    regen("dns")


@receiver(post_delete, sender=SOA)
def soa_post_delete(**_kwargs):
    """Regeneration dns après suppresson d'un SOA"""
    regen("dns")


@receiver(post_save, sender=Mx)
def mx_post_save(**_kwargs):
    """Regeneration dns après modification d'un MX"""
    regen("dns")


@receiver(post_delete, sender=Mx)
def mx_post_delete(**_kwargs):
    """Regeneration dns après suppresson d'un MX"""
    regen("dns")


@receiver(post_save, sender=Ns)
def ns_post_save(**_kwargs):
    """Regeneration dns après modification d'un NS"""
    regen("dns")


@receiver(post_delete, sender=Ns)
def ns_post_delete(**_kwargs):
    """Regeneration dns après modification d'un NS"""
    regen("dns")


@receiver(post_save, sender=Txt)
def text_post_save(**_kwargs):
    """Regeneration dns après modification d'un TXT"""
    regen("dns")


@receiver(post_delete, sender=Txt)
def text_post_delete(**_kwargs):
    """Regeneration dns après modification d'un TX"""
    regen("dns")


@receiver(post_save, sender=DName)
def dname_post_save(**_kwargs):
    """Updates the DNS regen after modification of a DName object."""
    regen("dns")


@receiver(post_delete, sender=DName)
def dname_post_delete(**_kwargs):
    """Updates the DNS regen after deletion of a DName object."""
    regen("dns")


@receiver(post_save, sender=Srv)
def srv_post_save(**_kwargs):
    """Regeneration dns après modification d'un SRV"""
    regen("dns")


@receiver(post_delete, sender=Srv)
def srv_post_delete(**_kwargs):
    """Regeneration dns après modification d'un SRV"""
    regen("dns")
