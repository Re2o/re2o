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
    """Machine.

    Attributes:
        user: the user who owns the machine.
        name: the name of the machine.
        active: whether the machine is active.
    """

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
        """Get the related interface and domain."""
        return chain(
            self.interface_set.all(),
            Domain.objects.filter(interface_parent__in=self.interface_set.all()),
        )

    @staticmethod
    def can_change_user(user_request, *_args, **_kwargs):
        """Check if an user is allowed to change the user who owns a
        Machine.

        Args:
            user_request: the user requesting to change owner.

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
        """Check if the user can view all machines.

        Args:
            user_request: the user requesting to view the machines.

        Returns:
            A tuple indicating whether the user can view all machines and a
            message if not.
        """
        if not user_request.has_perm("machines.view_machine"):
            return (
                False,
                _("You don't have the right to view all the machines."),
                ("machines.view_machine",),
            )
        return True, None, None

    @staticmethod
    def can_create(user_request, userid, *_args, **_kwargs):
        """Check if the user can create the machine, did not reach his quota
        and create a machine for themselves.

        Args:
            user_request: the user requesting to create the machine.
            userid: the ID of the owner of the machine to be created.

        Returns:
            A tuple indicating whether the user can create the machine and a
            message if not.
        """
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
        """Check if the user can edit the current instance of Machine (self).

        Args:
            user_request: the user requesting to edit self.

        Returns:
            A tuple indicating whether the user can edit self and a
            message if not.
        """
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
        """Check if the user can delete the current instance of Machine (self).

        Args:
            user_request: the user requesting to delete self.

        Returns:
            A tuple indicating whether the user can delete self and a
            message if not.
        """
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
        """Check if the user can view the current instance of Machine (self).

        Args:
            user_request: the user requesting to view self.

        Returns:
            A tuple indicating whether the user can view self and a
            message if not.
        """
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
        """Get the short name of the machine.

        By default, get the name of the first interface of the machine.
        """
        interfaces_set = self.interface_set.first()
        if interfaces_set:
            return str(interfaces_set.domain.name)
        else:
            return _("No name")

    @cached_property
    def complete_name(self):
        """Get the complete name of the machine.

        By default, get the name of the first interface of the machine.
        """
        return str(self.interface_set.first())

    @cached_property
    def all_short_names(self):
        """Get the short names of all interfaces of the machine."""
        return (
            Domain.objects.filter(interface_parent__machine=self)
            .values_list("name", flat=True)
            .distinct()
        )

    @cached_property
    def get_name(self):
        """Get the name of the machine.

        The name can be provided by the user, else the short name is used.
        """
        return self.name or self.short_name

    @classmethod
    def mass_delete(cls, machine_queryset):
        """Mass delete for machine queryset."""
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
        """Get the complete names of all interfaces of the machine."""
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
    """Machine type, related to an IP type and assigned to interfaces.

    Attributes:
        name: the name of the machine type.
        ip_type: the IP type of the machine type.
    """

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
        """Get all interfaces of the current machine type (self)."""
        return Interface.objects.filter(machine_type=self)

    def update_domains(self):
        """Update domains extension with the extension of interface_parent. Called after update of an ip_type or a machine_type object. Exceptions are handled in the views.
        (Calling domain.clear() for all domains could take several minutes)
        """
        Domain.objects.filter(interface_parent__machine_type=self).update(extension=self.ip_type.extension)

    @staticmethod
    def can_use_all(user_request, *_args, **_kwargs):
        """Check if an user can use all machine types.

        Args:
            user_request: the user requesting to use all machine types.

        Returns:
            A tuple with a boolean stating if user can access and an explanation
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
    """IP type, defining an IP range and assigned to machine types.

    Attributes:
        name: the name of the IP type.
        extension: the extension related to the IP type.
        need_infra: whether the 'infra' right is required.
        domaine_ip_start: the start IPv4 address of the IP type.
        domaine_ip_stop: the stop IPv4 address of the IP type.
        domaine_ip_network: the IPv4 network containg the IP range (optional).
        domaine_ip_netmask: the netmask of the domain's IPv4 range.
        reverse_v4: whether reverse DNS is enabled for IPv4.
        prefix_v6: the IPv6 prefix.
        prefix_v6_length: the IPv6 prefix length.
        reverse_v6: whether reverse DNS is enabled for IPv6.
        vlan: the VLAN related to the IP type.
        ouverture_ports: the ports opening list related to the IP type.
    """

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
        """Get the IPRange object from the current IP type."""
        return IPRange(self.domaine_ip_start, end=self.domaine_ip_stop)

    @cached_property
    def ip_set(self):
        """Get the IPSet object from the current IP type."""
        return IPSet(self.ip_range)

    @cached_property
    def ip_set_as_str(self):
        """Get the list of the IP addresses in the range as strings."""
        return [str(x) for x in self.ip_set]

    @cached_property
    def ip_set_cidrs_as_str(self):
        """Get the list of CIDRs from the IP range."""
        return [str(ip_range) for ip_range in self.ip_set.iter_cidrs()]

    @cached_property
    def ip_set_full_info(self):
        """Get the set of all information for IPv4.

        Iter over the CIDRs and get the network, broadcast etc.
        """
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
        """Get the set of all information for IPv6."""
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
        """Get the parent IP network of the range, if specified."""
        if self.domaine_ip_network:
            return IPNetwork(
                str(self.domaine_ip_network) + "/" + str(self.domaine_ip_netmask)
            )
        return None

    @cached_property
    def ip_net_full_info(self):
        """Get all information on the network including the range."""
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
        """Get the complete prefix v6 as CIDR."""
        return str(self.prefix_v6) + "/" + str(self.prefix_v6_length)

    def ip_objects(self):
        """Get all IPv4 objects related to the current IP type."""
        return IpList.objects.filter(ip_type=self)

    def free_ip(self):
        """Get all free IP addresses related to the current IP type."""
        return IpList.objects.filter(interface__isnull=True).filter(ip_type=self)

    def gen_ip_range(self):
        """Create the IpList objects related to the current IP type.

        Goes through the IP addresses on by one. If they already exist, update the
        type related to the IP addresses.
        """
        # Creation of the IP range in the IpList objects
        ip_obj = [IpList(ip_type=self, ipv4=str(ip)) for ip in self.ip_range]
        listes_ip = IpList.objects.filter(ipv4__in=[str(ip) for ip in self.ip_range])
        # If there are no IP addresses, create them
        if not listes_ip:
            IpList.objects.bulk_create(ip_obj)
        # Else, up the IP type
        else:
            listes_ip.update(ip_type=self)
        return

    def del_ip_range(self):
        """Deprecated method.

        Delete the IP range and the IpList in cascade.
        """
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
        """Replace the IPv6 prefixes of the interfaces related to the current
        IP type.
        """
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
        """Get the PTR records related to the current IP type, if reverse DNS
        is enabled for IPv4.
        """
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
        """Get the PTR records related to the current IP type, if reverse DNS
        is enabled for IPv6.
        """
        from re2o.utils import all_active_interfaces

        if self.reverse_v6:
            return all_active_interfaces(full=True).filter(machine_type__ip_type=self)
        else:
            return None

    def all_machine_types(self):
        """Get all machine types associated with this ip type (self)."""
        return MachineType.objects.filter(ip_type=self)

    def clean(self):
        """
        Check if:
            * ip_stop is after ip_start
            * the range is not more than a /16
            * the range is disjoint from existing ranges
            * the IPv6 prefix is formatted
        """
        if not self.domaine_ip_start or not self.domaine_ip_stop:
            raise ValidationError(_("Domaine IPv4 start and stop must be valid"))
        if IPAddress(self.domaine_ip_start) > IPAddress(self.domaine_ip_stop):
            raise ValidationError(_("Range end must be after range start..."))
        # The range should not be more than a /16
        if self.ip_range.size > 65536:
            raise ValidationError(
                _(
                    "The range is too large, you can't create"
                    " a larger one than a /16."
                )
            )
        # Check that the ranges do not overlap
        for element in IpType.objects.all().exclude(pk=self.pk):
            if not self.ip_set.isdisjoint(element.ip_set):
                raise ValidationError(
                    _("The specified range is not disjoint from existing" " ranges.")
                )
        # Format the IPv6 prefix
        if self.prefix_v6:
            self.prefix_v6 = str(IPNetwork(self.prefix_v6 + "/64").network)
        # Check if the domain network/netmask contains the domain IP start-stop
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
        """Check if the user can use all IP types without restrictions.

        Args:
            user_request: the user requesting to use all IP types.

        Returns:
            A tuple indicating whether the user can use all IP types and a
            message if not.
        """
        return (
            user_request.has_perm("machines.use_all_iptype"),
            None,
            ("machines.use_all_iptype",),
        )

    def __str__(self):
        return self.name


class Vlan(RevMixin, AclMixin, models.Model):
    """VLAN.

    The VLAN ID is limited between 0 and 4096.

    Attributes:
        vlan_id: the ID of the VLAN.
        name: the name of the VLAN.
        comment: the comment to describe the VLAN.
        arp_protect: whether ARP protection is enabled.
        dhcp_snooping: whether DHCP snooping is enabled.
        dhcpv6_snooping: whether DHCPv6 snooping is enabled.
        igmp: whether IGMP (v4 multicast management) is enabled.
        mld: whether MLD (v6 multicast management) is enabled.
    """

    vlan_id = models.PositiveIntegerField(validators=[MaxValueValidator(4095)])
    name = models.CharField(max_length=256)
    comment = models.CharField(max_length=256, blank=True)
    # Additional settings
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
    """NAS device, related to a machine type.

    Attributes:
        name: the name of the NAS device.
        nas_type: the type of the NAS device.
        machine_type: the machine type of the NAS device.
        port_access_mode: the access mode of the port related to the NAS
            device.
        autocapture_mac: whether MAC autocapture is enabled.
    """

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
    """SOA record.

    Default values come from the RIPE's recommendations here:
    https://www.ripe.net/publications/docs/ripe-203

    Attributes:
        name: the name of the SOA record.
        mail: the contact email address of the SOA record.
        refresh: the number of seconds before the secondary DNS need to
            refresh.
        retry: the number of seconds before the secondary DNS need to retry
            in case of timeout.
        expire: the number of seconds before the secondary DNS stop answering
            requests in case of timeout.
        ttl: the Time To Live of the SOA record.
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
        Get the following fields of the SOA record:
            * refresh
            * retry
            * expire
            * ttl
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
        """Get the contact email address formatted in the SOA record."""
        mail_fields = str(self.mail).split("@")
        return mail_fields[0].replace(".", "\\.") + "." + mail_fields[1] + "."

    @classmethod
    def new_default_soa(cls):
        """Create a new default SOA, useful for new extensions.

        /!\ Never delete or rename this function, it is used to make migrations
        of the database.
        """
        return cls.objects.get_or_create(
            name=_("SOA to edit"), mail="postmaster@example.com"
        )[0].pk


class Extension(RevMixin, AclMixin, models.Model):
    """Extension.

    DNS extension such as example.org.

    Attributes:
        name: the name of the extension.
        need_infra: whether the 'infra' right is required.
        origin: the A record (IpList) related to the extension.
        origin_v6: the AAAA record related to the extension.
        soa: the SOA record related to the extension.
    """

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
        """A DNS A and AAAA entry on origin for the current extension."""
        entry = ""
        if self.origin:
            entry += "@               IN  A       " + str(self.origin)
        if self.origin_v6:
            if entry:
                entry += "\n"
            entry += "@               IN  AAAA    " + str(self.origin_v6)
        return entry

    def get_associated_sshfp_records(self):
        """Get all SSHFP records related to the extension."""
        from re2o.utils import all_active_assigned_interfaces

        return (
            all_active_assigned_interfaces()
            .filter(machine_type__ip_type__extension=self)
            .filter(machine__id__in=SshFp.objects.values("machine"))
        )

    def get_associated_a_records(self):
        """Get all A records related to the extension."""
        from re2o.utils import all_active_assigned_interfaces

        return (
            all_active_assigned_interfaces()
            .filter(machine_type__ip_type__extension=self)
            .filter(ipv4__isnull=False)
        )

    def get_associated_aaaa_records(self):
        """Get all AAAA records related to the extension."""
        from re2o.utils import all_active_interfaces

        return all_active_interfaces(full=True).filter(
            machine_type__ip_type__extension=self
        )

    def get_associated_cname_records(self):
        """Get all CNAME records related to the extension."""
        from re2o.utils import all_active_assigned_interfaces

        return (
            Domain.objects.filter(extension=self)
            .filter(cname__interface_parent__in=all_active_assigned_interfaces())
            .prefetch_related("cname")
        )

    def get_associated_dname_records(self):
        """Get all DNAME records related to the extension."""
        return DName.objects.filter(alias=self)

    @staticmethod
    def can_use_all(user_request, *_args, **_kwargs):
        """Check if the user can use all extensions without restrictions.

        Args:
            user_request: the user requesting to use all extensions.

        Returns:
            A tuple indicating whether the user can use all extensions and a
            message if not.
        """
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
    """MX record.

    TODO link an MX record to an interface.

    Attributes:
        zone: the extension related to the MX record.
        priority: the priority of the MX record.
        name: the domain related to the MX record.
        ttl: the Time To Live of the MX record.
    """

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
        """Get the complete DNS entry of the MX record, to put in zone files.
        """
        return "@               IN  MX  {prior} {name}".format(
            prior=str(self.priority).ljust(3), name=str(self.name)
        )

    def __str__(self):
        return str(self.zone) + " " + str(self.priority) + " " + str(self.name)


class Ns(RevMixin, AclMixin, models.Model):
    """NS record.

    Attributes:
        zone: the extension related to the NS record.
        ns: the domain related to the NS record.
        ttl: the Time To Live of the NS record.
    """

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
        """Get the complete DNS entry of the NS record, to put in zone files.
        """
        return "@               IN  NS      " + str(self.ns)

    def __str__(self):
        return str(self.zone) + " " + str(self.ns)


class Txt(RevMixin, AclMixin, models.Model):
    """TXT record.

    Attributes:
        zone: the extension related to the TXT record.
        field1: the first field of the TXT record.
        field2: the second field of the TXT record.
        ttl: the Time To Live of the TXT record.
    """

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
        """Get the complete DNS entry of the TXT record, to put in zone files.
        """
        return str(self.field1).ljust(15) + " IN  TXT     " + str(self.field2)


class DName(RevMixin, AclMixin, models.Model):
    """DNAME record.

    Attributes:
        zone: the extension related to the DNAME record.
        alias: the alias of the DNAME record.
        ttl: the Time To Live of the DNAME record.
    """

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
        """Get the complete DNS entry of the TXT record, to put in zone files.
        """
        return str(self.alias).ljust(15) + " IN  DNAME   " + str(self.zone)


class Srv(RevMixin, AclMixin, models.Model):
    """SRV record.

    Attributes:
        service: the name of the service of the SRV record.
        protocole: the protocol of the service of the SRV record.
        extension: the extension of the SRV record.
        ttl: the Time To Live of the SRV record.
        priority: the priority of the target server.
        weight: the relative weight for records with the same priority.
        port: the TCP/UDP port of the SRV record.
        target: the target server of the SRV record.
    """

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
        """Get the complete DNS entry of the SRV record, to put in zone files.
        """
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
    """SSH public key fingerprint.

    Attributes:
        machine: the machine related to the SSH fingerprint.
        pub_key_entry: the SSH public key related to the SSH fingerprint.
        algo: the algorithm used for the SSH fingerprint.
        comment: the comment to describe the SSH fingerprint.
    """

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
        """Get the ID of the algorithm for this key."""
        if "ecdsa" in self.algo:
            return 3
        elif "rsa" in self.algo:
            return 1
        else:
            return 2

    @cached_property
    def hash(self):
        """Get the hashes for the pub key with correct ID.

        See RFC: 1 is sha1 , 2 is sha256.
        """
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
    """Interface, the key object of the app machines.

    Attributes:
        ipv4: the IPv4 address (IpList) of the interface.
        mac_address: the MAC address of the interface.
        machine: the machine to which the interface belongs.
        machine_type: the machine type of the interface.
        details: the details to describe the interface.
        port_lists: the ports opening list of the interface.
    """

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
        """Get the state of the interface.

        The interface is active if the related machine is active and the owner
        has access.
        """
        machine = self.machine
        user = self.machine.user
        return machine.active and user.has_access()

    @cached_property
    def ipv6_slaac(self):
        """Get the IPv6 type object from the prefix related to the parent IP
        type.
        """
        if self.machine_type.ip_type.prefix_v6:
            return EUI(self.mac_address).ipv6(
                IPNetwork(self.machine_type.ip_type.prefix_v6).network
            )
        else:
            return None

    @cached_property
    def gen_ipv6_dhcpv6(self):
        """Create an IPv6 address to assign with DHCPv6."""
        prefix_v6 = self.machine_type.ip_type.prefix_v6.encode().decode("utf-8")
        if not prefix_v6:
            return None
        return IPv6Address(
            IPv6Address(prefix_v6).exploded[:20] + IPv6Address(self.id).exploded[20:]
        )

    @cached_property
    def get_vendor(self):
        """Get the vendor from the MAC address of the interface."""
        mac = EUI(self.mac_address)
        try:
            oui = mac.oui
            vendor = oui.registration().org
        except (IndexError, NotRegisteredError) as error:
            vendor = _("Unknown vendor.")
        return vendor

    def sync_ipv6_dhcpv6(self):
        """Assign an IPv6 address by DHCPv6, computed from the interface's ID.
        """
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
        """Create, update and delete if necessary the IPv6 SLAAC related to the
        interface.
        """
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
        """Create and update the IPv6 addresses according to the IPv6 mode set.
        """
        if preferences.models.OptionalMachine.get_cached_value("ipv6_mode") == "SLAAC":
            self.sync_ipv6_slaac()
        elif (
            preferences.models.OptionalMachine.get_cached_value("ipv6_mode") == "DHCPV6"
        ):
            self.sync_ipv6_dhcpv6()
        else:
            return

    def ipv6(self):
        """Get the queryset of the IPv6 addresses list.

        The IPv6 SLAAC is returned only if SLAAC mode is enabled (and not
        DHCPv6).
        """
        if preferences.models.OptionalMachine.get_cached_value("ipv6_mode") == "SLAAC":
            return self.ipv6list.all()
        elif (
            preferences.models.OptionalMachine.get_cached_value("ipv6_mode") == "DHCPV6"
        ):
            return self.ipv6list.filter(slaac_ip=False)
        else:
            return []

    def mac_bare(self):
        """Get the mac_bare formatted MAC address."""
        return str(EUI(self.mac_address, dialect=mac_bare)).lower()

    def filter_macaddress(self):
        """Format the MAC address as mac_bare.

        Raises:
            ValidationError: the MAC address cannot be formatted as mac_bare.
        """
        try:
            self.mac_address = str(EUI(self.mac_address, dialect=default_dialect()))
        except:
            raise ValidationError(_("The given MAC address is invalid."))

    def assign_ipv4(self):
        """Assign an IPv4 address to the interface."""
        free_ips = self.machine_type.ip_type.free_ip()
        if free_ips:
            self.ipv4 = free_ips[0]
        else:
            raise ValidationError(
                _("There are no IP addresses available in the slash.")
            )
        return

    def unassign_ipv4(self):
        """Unassign the IPv4 address of the interface."""
        self.ipv4 = None

    @classmethod
    def mass_unassign_ipv4(cls, interface_list):
        """Unassign IPv4 addresses to multiple interfaces.

        Args:
            interface_list: the list of interfaces to be updated.
        """
        with transaction.atomic(), reversion.create_revision():
            interface_list.update(ipv4=None)
            reversion.set_comment("IPv4 unassignment")

    @classmethod
    def mass_assign_ipv4(cls, interface_list):
        """Assign IPv4 addresses to multiple interfaces.

        Args:
            interface_list: the list of interfaces to be updated.
        """
        for interface in interface_list:
            with transaction.atomic(), reversion.create_revision():
                interface.assign_ipv4()
                interface.save()
                reversion.set_comment("IPv4 assignment")

    def all_domains(self):
        """Get all domains associated with this interface (self)."""
        return Domain.objects.filter(interface_parent=self)

    def update_type(self):
        """Reassign addresses when the IP type of the machine type changed."""
        self.clean()
        self.save()

    def has_private_ip(self):
        """Check if the IPv4 address assigned is private."""
        if self.ipv4:
            return IPAddress(str(self.ipv4)).is_private()
        else:
            return False

    def may_have_port_open(self):
        """Check if the interface has a public IP address."""
        return self.ipv4 and not self.has_private_ip()

    def clean(self, *args, **kwargs):
        """Format the MAC address as mac_bare (see filter_mac) and assign an
        IPv4 address in the appropriate range if the current address is
        nonexistent or inconsistent.

        If type was an invalid value, django won't create an attribute type
        but try clean() as we may be able to create it from another value so
        even if the error as yet been detected at this point, django continues
        because the error might not prevent us from creating the instance. But
        in our case, it's impossible to create a type value so we raise the
        error.
        """
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
        # Check the consistency by forcing the extension
        if self.ipv4:
            if self.machine_type.ip_type != self.ipv4.ip_type:
                raise ValidationError(
                    _("The IPv4 address and the machine type don't match.")
                )
        self.validate_unique()
        super(Interface, self).save(*args, **kwargs)

    @staticmethod
    def can_create(user_request, machineid, *_args, **_kwargs):
        """Check if the user can create an interface, or that the machine is
        owned by the user.

        Args:
            user_request: the user requesting to create the interface.
            machineid: the ID of the machine related to the interface.

        Returns:
            A tuple indicating whether the user can create the interface and a
            message if not.
        """
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
        """Check if the user can edit the machine.
        Args:
            user_request: the user requesting to edit the machine.

        Returns:
            A tuple indicating whether the user can edit the machine and a
            message if not.
        """
        can = user_request.has_perm("machines.change_interface_machine")
        return (
            can,
            _("You don't have the right to edit the machine.") if not can else None,
            ("machines.change_interface_machine",),
        )

    def can_edit(self, user_request, *args, **kwargs):
        """Check if the user can edit the current interface (self), or that it
        is owned by the user.

        Args:
            user_request: the user requesting to edit self.

        Returns:
            A tuple indicating whether the user can edit self and a
            message if not.
        """
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
        """Check if the user can delete the current interface (self), or that
        it is owned by the user.

        Args:
            user_request: the user requesting to delete self.

        Returns:
            A tuple indicating whether the user can delete self and a
            message if not.
        """
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
        """Check if the user can view the current interface (self), or that it
        is owned by the user.

        Args:
            user_request: the user requesting to view self.

        Returns:
            A tuple indicating whether the user can view self and a
            message if not.
        """
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
    """IPv6 addresses list.

    Args:
        ipv6: the IPv6 address of the list.
        interface: the interface related to the list.
        slaac_ip: whether SLAAC mode is enabled.
        active: whether the ip is to be used.
    """

    ipv6 = models.GenericIPAddressField(protocol="IPv6")
    interface = models.ForeignKey(
        "Interface", on_delete=models.CASCADE, related_name="ipv6list"
    )
    slaac_ip = models.BooleanField(default=False)
    active = models.BooleanField(
        default=True,
        help_text=_("If false,the DNS will not provide this ip.")
    )

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
        """Check if the user can create an IPv6 address for the given
        interface, or that it is owned by the user.

        Args:
            user_request: the user requesting to create an IPv6 address.
            interfaceid: the ID of the interface to be edited.

        Returns:
            A tuple indicating whether the user can create an IPv6 address for
            the given interface and a message if not.
        """
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
        """Check if a user can change the SLAAC value."""
        can = user_request.has_perm("machines.change_ipv6list_slaac_ip")
        return (
            can,
            _("You don't have the right to change the SLAAC value of an IPv6 address.")
            if not can
            else None,
            ("machines.change_ipv6list_slaac_ip",),
        )

    def can_edit(self, user_request, *args, **kwargs):
        """Check if the user can edit the current IPv6 addresses list (self),
        or that the related interface is owned by the user.

        Args:
            user_request: the user requesting to edit self.

        Returns:
            A tuple indicating whether the user can edit self and a
            message if not.
        """
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
        """Check if the user can delete the current IPv6 addresses list (self),
        or that the related interface is owned by the user.

        Args:
            user_request: the user requesting to delete self.

        Returns:
            A tuple indicating whether the user can delete self and a
            message if not.
        """
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
        """Check if the user can view the current IPv6 addresses list (self),
        or that the related interface is owned by the user.

        Args:
            user_request: the user requesting to view self.

        Returns:
            A tuple indicating whether the user can view self and a
            message if not.
        """
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
        """Check if the IPv6 prefix is correct and update it if not."""
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
        """Force the call to clean before saving."""
        self.full_clean()
        super(Ipv6List, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.ipv6)


class Domain(RevMixin, AclMixin, FieldPermissionModelMixin, models.Model):
    """Domain.

    A and CNAME records at the same time: it enables to store aliases and
    machine names, according to which fields are used.

    Attributes:
        interface_parent: the parent interface of the domain.
        name: the name of the domain (mandatory and unique).
        extension: the extension of the domain.
        cname: the CNAME record related to the domain.
        ttl: the Time To Live of the domain.
    """

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
        """Get the extension of the domain.

        If it is an A record, get the extension of the parent interface.
        If it is a CNAME record, get the extension of self.
        """
        if self.interface_parent:
            return self.interface_parent.machine_type.ip_type.extension
        elif hasattr(self, "extension"):
            return self.extension
        else:
            return None

    def clean(self):
        """
        Check if:
            * the object is either an A or a CNAME record
            * the CNAME record does not point to itself
            * the name is not over 63 characters
            * the name does not contain forbidden characters
            * the couple (name, extension) is unique
        """
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
        """Get the DNS entry of the domain."""
        if self.cname:
            return "{name} IN CNAME   {cname}.".format(
                name=str(self.name).ljust(15), cname=str(self.cname)
            )

    def save(self, *args, **kwargs):
        """Prevent from saving if the extension is invalid and force the call
        to clean before saving.
        """
        if not self.get_extension():
            raise ValidationError(_("Invalid extension."))
        self.full_clean()
        super(Domain, self).save(*args, **kwargs)

    @cached_property
    def get_source_interface(self):
        """Get the source interface of the domain.

        If it is an A record, get the parent interface.
        If it is a CNAME record, follow recursively until reaching the related
        A record and get the parent interface.
        """
        if self.interface_parent:
            return self.interface_parent
        else:
            return self.cname.get_source_interface

    @staticmethod
    def can_create(user_request, interfaceid, *_args, **_kwargs):
        """Check if the user can create a domain for the given interface, or
        that it is owned by the user.

        Args:
            user_request: the user requesting to create a domain.
            interfaceid: the ID of the interface to be edited.

        Returns:
            A tuple indicating whether the user can create a domain for
            the given interface and a message if not.
        """
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
        """Check if the user can edit the current domain, or that the related
        interface is owned by the user.

        Args:
            user_request: the user requesting to edit self.

        Returns:
            A tuple indicating whether the user can edit self and a
            message if not.
        """
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
        """Check if the user can delete the current domain, or that the related
        interface is owned by the user.

        Args:
            user_request: the user requesting to delete self.

        Returns:
            A tuple indicating whether the user can delete self and a
            message if not.
        """
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
        """Check if the user can view the current domain, or that the related
        interface is owned by the user.

        Args:
            user_request: the user requesting to view self.

        Returns:
            A tuple indicating whether the user can view self and a
            message if not.
        """
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
        """Check if the user can change the TTL of the domain."""
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
    """IPv4 addresses list.

    Attributes:
        ipv4: the IPv4 address of the list.
        ip_type: the IP type of the list.
    """

    ipv4 = models.GenericIPAddressField(protocol="IPv4", unique=True)
    ip_type = models.ForeignKey("IpType", on_delete=models.CASCADE)

    class Meta:
        permissions = (("view_iplist", _("Can view an IPv4 addresses list object")),)
        verbose_name = _("IPv4 addresses list")
        verbose_name_plural = _("IPv4 addresses lists")

    @cached_property
    def need_infra(self):
        """Check if the 'infra' right is required to assign this IP address.
        """
        return self.ip_type.need_infra

    def clean(self):
        """Clean self.

        Raises:
            ValidationError: if the IPv4 address and the IP type of self do not
            match.
        """
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
    """Role.

    It enabled to automate the generation of server configurations.

    Attributes:
        role_type: the type of the role (name provided by the user).
        servers: the servers related to the role.
        specific_role: the specific role, e.g. DHCP server, LDAP server etc.
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
    """Service (DHCP, DNS...).

    Attributes:
        service_type: the type of the service (provided by the user).
        min_time_regen: the minimal time before regeneration.
        regular_time_regen: the maximal time before regeneration.
        servers: the servers related to the service.
    """

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
        """Set the demand for regen to True for the current Service (self)."""
        Service_link.objects.filter(service=self).exclude(asked_regen=True).update(
            asked_regen=True
        )
        return

    def process_link(self, servers):
        """Process the links between services and servers.

        Django does not create the ManyToMany relations with explicit
        intermediate table.
        """
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
    """Ask regeneration for the given service.

    Args:
        service: the service to be regenerated.
    """
    obj = Service.objects.filter(service_type=service)
    if obj:
        obj[0].ask_regen()
    return


class Service_link(RevMixin, AclMixin, models.Model):
    """Service server link.

    Attributes:
        service: the service related to the link.
        server: the server related to the link.
        last_regen: datetime, the last time of the regeneration.
        asked_regen: whether regeneration has been asked.
    """

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
        """Update the regen information when the server regenerated its
        service."""
        self.last_regen = timezone.now()
        self.asked_regen = False
        self.save()

    @property
    def need_regen(self):
        """Decide if the minimal time elapsed is enough to regenerate the
        service."""
        return bool(
            (
                self.asked_regen
                and (self.last_regen + self.service.min_time_regen) < timezone.now()
            )
            or (self.last_regen + self.service.regular_time_regen) < timezone.now()
        )

    @need_regen.setter
    def need_regen(self, value):
        """Force to set the need_regen value.

        True means a regen is asked and False means a regen has been done.

        Args:
            value: bool, the value to set.
        """
        if not value:
            self.last_regen = timezone.now()
        self.asked_regen = value
        self.save()

    def __str__(self):
        return str(self.server) + " " + str(self.service)


class OuverturePortList(RevMixin, AclMixin, models.Model):
    """Ports opening list.

    Attributes:
        name: the name of the ports configuration.
    """

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
        """Check if the user can delete the current ports opening list (self).

        Args:
            user_request: the user requesting to delete self.

        Returns:
            A tuple indicating whether the user can delete self and a
            message if not.
        """
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
        """Get the list of ports opened in TCP IN of the current ports opening
        list."""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.TCP, io=OuverturePort.IN
        )

    def udp_ports_in(self):
        """Get the list of ports opened in UDP IN of the current ports opening
        list."""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.UDP, io=OuverturePort.IN
        )

    def tcp_ports_out(self):
        """Get the list of ports opened in TCP OUT of the current ports opening
        list."""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.TCP, io=OuverturePort.OUT
        )

    def udp_ports_out(self):
        """Get the list of ports opened in UDP OUT of the current ports opening
        list."""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.UDP, io=OuverturePort.OUT
        )


class OuverturePort(RevMixin, AclMixin, models.Model):
    """Ports opening.

    The ports of the range are between begin and end (included).
    If begin == end, then it represents a single port.
    The ports are limited to be between 0 and 65535, as defined in the RFC.

    Attributes:
        begin: the number of the first port of the ports opening.
        end: the number of the last port of the ports opening.
        port_list: the ports opening list (configuration for opened ports) of
            the ports opening.
        protocole: the protocol of the ports opening.
        io: the direction of communication, IN or OUT.
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
        """Format the ports opening by calling str."""
        return str(self)


@receiver(post_save, sender=Machine)
def machine_post_save(**kwargs):
    """Synchronise LDAP and regen firewall/DHCP after a machine is edited."""
    user = kwargs["instance"].user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)
    regen("dhcp")
    regen("mac_ip_list")


@receiver(post_delete, sender=Machine)
def machine_post_delete(**kwargs):
    """Synchronise LDAP and regen firewall/DHCP after a machine is deleted."""
    machine = kwargs["instance"]
    user = machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)
    regen("dhcp")
    regen("mac_ip_list")


@receiver(post_save, sender=Interface)
def interface_post_save(**kwargs):
    """Synchronise LDAP, regen firewall/DHCP after an interface is edited
    and update associated domains
    """
    interface = kwargs["instance"]
    interface.sync_ipv6()
    user = interface.machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)
    # Regen services
    regen("dhcp")
    regen("mac_ip_list")
    # Update associated domains
    for domain in interface.all_domains():
        domain.clean()
        domain.save()


@receiver(post_delete, sender=Interface)
def interface_post_delete(**kwargs):
    """Synchronise LDAP and regen firewall/DHCP after an interface is deleted.
    """
    interface = kwargs["instance"]
    user = interface.machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)


@receiver(post_save, sender=IpType)
def iptype_post_save(**kwargs):
    """Generate the IP objects after an IP type is edited."""
    iptype = kwargs["instance"]
    iptype.gen_ip_range()
    iptype.check_replace_prefixv6()
    for machinetype in iptype.all_machine_types():
        machinetype.save()


@receiver(post_save, sender=MachineType)
def machinetype_post_save(**kwargs):
    """Update the interfaces after the machine type is changed (change the
    parent IP type).
    """
    machinetype = kwargs["instance"]
    machinetype.update_domains()


@receiver(post_save, sender=Domain)
def domain_post_save(**_kwargs):
    """Regenerate the DNS after a domain is edited."""
    regen("dns")


@receiver(post_delete, sender=Domain)
def domain_post_delete(**_kwargs):
    """Regenerate the DNS after a domain is deleted."""
    regen("dns")


@receiver(post_save, sender=Extension)
def extension_post_save(**_kwargs):
    """Regenerate the DNS after an extension is edited."""
    regen("dns")


@receiver(post_delete, sender=Extension)
def extension_post_delete(**_kwargs):
    """Regenerate the DNS after an extension is deleted."""
    regen("dns")


@receiver(post_save, sender=SOA)
def soa_post_save(**_kwargs):
    """Regenerate the DNS after a SOA record is edited."""
    regen("dns")


@receiver(post_delete, sender=SOA)
def soa_post_delete(**_kwargs):
    """Regenerate the DNS after a SOA record is deleted."""
    regen("dns")


@receiver(post_save, sender=Mx)
def mx_post_save(**_kwargs):
    """Regenerate the DNS after an MX record is edited."""
    regen("dns")


@receiver(post_delete, sender=Mx)
def mx_post_delete(**_kwargs):
    """Regenerate the DNS after an MX record is deleted."""
    regen("dns")


@receiver(post_save, sender=Ns)
def ns_post_save(**_kwargs):
    """Regenerate the DNS after an NS record is edited."""
    regen("dns")


@receiver(post_delete, sender=Ns)
def ns_post_delete(**_kwargs):
    """Regenerate the DNS after an NS record is deleted."""
    regen("dns")


@receiver(post_save, sender=Txt)
def text_post_save(**_kwargs):
    """Regenerate the DNS after a TXT record is edited."""
    regen("dns")


@receiver(post_delete, sender=Txt)
def text_post_delete(**_kwargs):
    """Regenerate the DNS after a TXT record is deleted."""
    regen("dns")


@receiver(post_save, sender=DName)
def dname_post_save(**_kwargs):
    """Regenerate the DNS after a DNAME record is edited."""
    regen("dns")


@receiver(post_delete, sender=DName)
def dname_post_delete(**_kwargs):
    """Regenerate the DNS after a DNAME record is deleted."""
    regen("dns")


@receiver(post_save, sender=Srv)
def srv_post_save(**_kwargs):
    """Regenerate the DNS after an SRV record is edited."""
    regen("dns")


@receiver(post_delete, sender=Srv)
def srv_post_delete(**_kwargs):
    """Regenerate the DNS after an SRV record is deleted."""
    regen("dns")
