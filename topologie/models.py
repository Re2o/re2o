# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
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
Definition des modèles de l'application topologie.

On défini les models suivants :

- stack (id, id_min, id_max et nom) regrouppant les switches
- switch : nom, nombre de port, et interface
machine correspondante (mac, ip, etc) (voir machines.models.interface)
- Port: relié à un switch parent par foreign_key, numero du port,
relié de façon exclusive à un autre port, une machine
(serveur ou borne) ou une prise murale
- room : liste des prises murales, nom et commentaire de l'état de
la prise
"""

from __future__ import unicode_literals

import itertools

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.functional import cached_property
from django.core.cache import cache
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from reversion import revisions as reversion

from preferences.models import OptionalTopologie, RadiusKey, SwitchManagementCred
from machines.models import Machine, regen, Role, MachineType, Ipv6List
from re2o.mixins import AclMixin, RevMixin


class Stack(AclMixin, RevMixin, models.Model):
    """Un objet stack. Regrouppe des switchs en foreign key
    ,contient une id de stack, un switch id min et max dans
    le stack"""

    name = models.CharField(max_length=32, blank=True, null=True)
    stack_id = models.CharField(max_length=32, unique=True)
    details = models.CharField(max_length=255, blank=True, null=True)
    member_id_min = models.PositiveIntegerField()
    member_id_max = models.PositiveIntegerField()

    class Meta:
        permissions = (("view_stack", _("Can view a stack object")),)
        verbose_name = _("switches stack")
        verbose_name_plural = _("switches stacks")

    def __str__(self):
        return " ".join([self.name, self.stack_id])

    def save(self, *args, **kwargs):
        self.clean()
        if not self.name:
            self.name = self.stack_id
        super(Stack, self).save(*args, **kwargs)

    def clean(self):
        """ Verification que l'id_max < id_min"""
        if self.member_id_max < self.member_id_min:
            raise ValidationError(
                {"member_id_max": _("The maximum ID is less than the minimum ID.")}
            )


class AccessPoint(Machine):
    """Define a wireless AP. Inherit from machines.interfaces

    Definition pour une borne wifi , hérite de machines.interfaces
    """

    location = models.CharField(
        max_length=255,
        help_text=_("Details about the AP's location."),
        blank=True,
        null=True,
    )

    class Meta:
        permissions = (("view_accesspoint", _("Can view an access point object")),)
        verbose_name = _("access point")
        verbose_name_plural = _("access points")

    def port(self):
        """Return the queryset of ports for this device"""
        return Port.objects.filter(machine_interface__machine=self)

    def switch(self):
        """Return the switch where this is plugged"""
        return Switch.objects.filter(ports__machine_interface__machine=self)

    def building(self):
        """
        Return the building of the AP/Server (building of the switchs
        connected to...)
        """
        return Building.objects.filter(switchbay__switch=self.switch())

    @cached_property
    def short_name(self):
        return str(self.interface_set.first().domain.name)

    @classmethod
    def all_ap_in(cls, building_instance):
        """Get a building as argument, returns all ap of a building"""
        return cls.objects.filter(
            interface__port__switch__switchbay__building=building_instance
        )

    def __str__(self):
        return str(self.interface_set.first())

    # We want to retrieve the default behaviour given by AclMixin rather
    # than the one overwritten by Machine. If you are not familiar with
    # the behaviour of `super`, please check https://docs.python.org/3/library/functions.html#super

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return super(Machine, cls).get_instance(*args, **kwargs)

    @classmethod
    def can_create(cls, *args, **kwargs):
        return super(Machine, cls).can_create(*args, **kwargs)

    def can_edit(self, *args, **kwargs):
        return super(Machine, self).can_edit(*args, **kwargs)

    def can_delete(self, *args, **kwargs):
        return super(Machine, self).can_delete(*args, **kwargs)

    def can_view(self, *args, **kwargs):
        return super(Machine, self).can_view(*args, **kwargs)


class Server(Machine):
    """
    Dummy class, to retrieve servers of a building, or get switch of a server
    """

    class Meta:
        proxy = True

    def port(self):
        """Return the queryset of ports for this device"""
        return Port.objects.filter(machine_interface__machine=self)

    def switch(self):
        """Return the switch where this is plugged"""
        return Switch.objects.filter(ports__machine_interface__machine=self)

    def building(self):
        """
        Return the building of the AP/Server
        (building of the switchs connected to...)
        """
        return Building.objects.filter(switchbay__switch=self.switch())

    @cached_property
    def short_name(self):
        return str(self.interface_set.first().domain.name)

    @classmethod
    def all_server_in(cls, building_instance):
        """Get a building as argument, returns all server of a building"""
        return cls.objects.filter(
            interface__port__switch__switchbay__building=building_instance
        ).exclude(accesspoint__isnull=False)

    def __str__(self):
        return str(self.interface_set.first())

    # We want to retrieve the default behaviour given by AclMixin rather
    # than the one overwritten by Machine. If you are not familiar with
    # the behaviour of `super`, please check https://docs.python.org/3/library/functions.html#super

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return super(Machine, cls).get_instance(*args, **kwargs)

    @classmethod
    def can_create(cls, *args, **kwargs):
        return super(Machine, cls).can_create(*args, **kwargs)

    def can_edit(self, *args, **kwargs):
        return super(Machine, self).can_edit(*args, **kwargs)

    def can_delete(self, *args, **kwargs):
        return super(Machine, self).can_delete(*args, **kwargs)

    def can_view(self, *args, **kwargs):
        return super(Machine, self).can_view(*args, **kwargs)


class Switch(Machine):
    """ Definition d'un switch. Contient un nombre de ports (number),
    un emplacement (location), un stack parent (optionnel, stack)
    et un id de membre dans le stack (stack_member_id)
    relié en onetoone à une interface
    Pourquoi ne pas avoir fait hériter switch de interface ?
    Principalement par méconnaissance de la puissance de cette façon de faire.
    Ceci étant entendu, django crée en interne un onetoone, ce qui a un
    effet identique avec ce que l'on fait ici

    Validation au save que l'id du stack est bien dans le range id_min
    id_max de la stack parente"""

    number = models.PositiveIntegerField(help_text=_("Number of ports."))
    stack = models.ForeignKey(
        "topologie.Stack", blank=True, null=True, on_delete=models.SET_NULL
    )
    stack_member_id = models.PositiveIntegerField(blank=True, null=True)
    model = models.ForeignKey(
        "topologie.ModelSwitch",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_("Switch model."),
    )
    switchbay = models.ForeignKey(
        "topologie.SwitchBay", blank=True, null=True, on_delete=models.SET_NULL
    )
    radius_key = models.ForeignKey(
        "preferences.RadiusKey",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text=_("RADIUS key of the switch."),
    )
    management_creds = models.ForeignKey(
        "preferences.SwitchManagementCred",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text=_("Management credentials for the switch."),
    )
    automatic_provision = models.BooleanField(
        default=False, help_text=_("Automatic provision for the switch.")
    )

    class Meta:
        unique_together = ("stack", "stack_member_id")
        permissions = (("view_switch", _("Can view a switch object")),)
        verbose_name = _("switch")
        verbose_name_plural = _("switches")

    def clean(self):
        """ Verifie que l'id stack est dans le bon range
        Appelle également le clean de la classe parente"""
        super(Switch, self).clean()
        if self.stack is not None:
            if self.stack_member_id is not None:
                if (self.stack_member_id > self.stack.member_id_max) or (
                    self.stack_member_id < self.stack.member_id_min
                ):
                    raise ValidationError(
                        {
                            "stack_member_id": _(
                                "The switch ID exceeds the"
                                " limits allowed by the stack."
                            )
                        }
                    )
            else:
                raise ValidationError(
                    {"stack_member_id": _("The stack member ID can't be void.")}
                )

    def create_ports(self, begin, end):
        """ Crée les ports de begin à end si les valeurs données
        sont cohérentes. """
        if end < begin:
            raise ValidationError(_("The end port is less than the start port."))
        ports_to_create = range(begin, end + 1)
        existing_ports = Port.objects.filter(switch=self.switch).values_list(
            "port", flat=True
        )
        non_existing_ports = list(set(ports_to_create) - set(existing_ports))

        if len(non_existing_ports) + existing_ports.count() > self.number:
            raise ValidationError(_("This switch can't have that many ports."))
        with transaction.atomic(), reversion.create_revision():
            reversion.set_comment("Creation")
            Port.objects.bulk_create(
                [
                    Port(switch=self.switch, port=port_id)
                    for port_id in non_existing_ports
                ]
            )

    def main_interface(self):
        """ Returns the 'main' interface of the switch
        It must the the management interface for that device"""
        switch_iptype = OptionalTopologie.get_cached_value("switchs_ip_type")
        if switch_iptype:
            return (
                self.interface_set.filter(machine_type__ip_type=switch_iptype).first()
                or self.interface_set.first()
            )
        return self.interface_set.first()

    @cached_property
    def get_name(self):
        return self.name or getattr(self.main_interface(), "domain", "Unknown")

    @cached_property
    def get_radius_key(self):
        """Retourne l'objet de la clef radius de ce switch"""
        return self.radius_key or RadiusKey.objects.filter(default_switch=True).first()

    @cached_property
    def get_radius_key_value(self):
        """Retourne la valeur en str de la clef radius, none si il n'y en a pas"""
        if self.get_radius_key:
            return self.get_radius_key.radius_key
        else:
            return None

    @cached_property
    def get_radius_servers_objects(self):
        return Role.all_interfaces_for_roletype("radius-server").filter(
            machine_type__in=MachineType.objects.filter(
                interface__in=self.interface_set.all()
            )
        )

    @cached_property
    def get_radius_servers(self):
        def return_ips_dict(interfaces):
            return {
                "ipv4": [str(interface.ipv4) for interface in interfaces],
                "ipv6": Ipv6List.objects.filter(interface__in=interfaces).values_list(
                    "ipv6", flat=True
                ),
            }

        return return_ips_dict(self.get_radius_servers_objects)

    @cached_property
    def get_management_cred(self):
        """Retourne l'objet des creds de managament de ce switch"""
        return (
            self.management_creds
            or SwitchManagementCred.objects.filter(default_switch=True).first()
        )

    @cached_property
    def get_management_cred_value(self):
        """Retourne un dict des creds de management du switch"""
        if self.get_management_cred:
            return {
                "id": self.get_management_cred.management_id,
                "pass": self.get_management_cred.management_pass,
            }
        else:
            return None

    @cached_property
    def rest_enabled(self):
        return (
            OptionalTopologie.get_cached_value("switchs_rest_management")
            or self.automatic_provision
        )

    @cached_property
    def web_management_enabled(self):
        sw_management = OptionalTopologie.get_cached_value("switchs_web_management")
        sw_management_ssl = OptionalTopologie.get_cached_value(
            "switchs_web_management_ssl"
        )
        if sw_management_ssl:
            return "ssl"
        elif sw_management:
            return "plain"
        else:
            return self.automatic_provision

    @cached_property
    def ipv4(self):
        """Return the switch's management ipv4"""
        return str(self.main_interface().ipv4)

    @cached_property
    def ipv6(self):
        """Returne the switch's management ipv6"""
        return str(self.main_interface().ipv6().first())

    @cached_property
    def interfaces_subnet(self):
        """Return dict ip:subnet for all ip of the switch"""
        return dict(
            (
                str(interface.ipv4),
                interface.machine_type.ip_type.ip_net_full_info
                or interface.machine_type.ip_type.ip_set_full_info[0],
            )
            for interface in self.interface_set.all()
        )

    @cached_property
    def interfaces6_subnet(self):
        """Return dict ip6:subnet for all ipv6 of the switch"""
        return dict(
            (
                str(interface.ipv6().first()),
                interface.machine_type.ip_type.ip6_set_full_info,
            )
            for interface in self.interface_set.all()
        )

    @cached_property
    def list_modules(self):
        """Return modules of that switch, list of dict (rank, reference)"""
        modules = []
        if getattr(self.model, "is_modular", None):
            if self.model.is_itself_module:
                modules.append((1, self.model.reference))
            for module_of_self in self.moduleonswitch_set.all():
                modules.append((module_of_self.slot, module_of_self.module.reference))
        return modules

    @cached_property
    def get_dormitory(self):
        """Returns the dormitory of that switch"""
        if self.switchbay:
            return self.switchbay.building.dormitory
        else:
            return None

    @classmethod
    def nothing_profile(cls):
        """Return default nothing port profile"""
        nothing_profile, _created = PortProfile.objects.get_or_create(
            profil_default="nothing", name="nothing", radius_type="NO"
        )
        return nothing_profile

    def profile_type_or_nothing(self, profile_type):
        """Return the profile for a profile_type of this switch

        If exists, returns the defined default profile for a profile type on the dormitory which
        the switch belongs

        Otherwise, returns the nothing profile"""
        profile_queryset = PortProfile.objects.filter(profil_default=profile_type)
        if self.get_dormitory:
            port_profile = (
                profile_queryset.filter(on_dormitory=self.get_dormitory).first()
                or profile_queryset.first()
            )
        else:
            port_profile = profile_queryset.first()
        return port_profile or Switch.nothing_profile()

    @cached_property
    def default_uplink_profile(self):
        """Default uplink profile for that switch -- in cache"""
        return self.profile_type_or_nothing("uplink")

    @cached_property
    def default_access_point_profile(self):
        """Default ap profile for that switch -- in cache"""
        return self.profile_type_or_nothing("access_point")

    @cached_property
    def default_room_profile(self):
        """Default room profile for that switch -- in cache"""
        return self.profile_type_or_nothing("room")

    @cached_property
    def default_asso_machine_profile(self):
        """Default asso machine profile for that switch -- in cache"""
        return self.profile_type_or_nothing("asso_machine")

    def __str__(self):
        return str(self.get_name)

    # We want to retrieve the default behaviour given by AclMixin rather
    # than the one overwritten by Machine. If you are not familiar with
    # the behaviour of `super`, please check https://docs.python.org/3/library/functions.html#super

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return super(Machine, cls).get_instance(*args, **kwargs)

    @classmethod
    def can_create(cls, *args, **kwargs):
        return super(Machine, cls).can_create(*args, **kwargs)

    def can_edit(self, *args, **kwargs):
        return super(Machine, self).can_edit(*args, **kwargs)

    def can_delete(self, *args, **kwargs):
        return super(Machine, self).can_delete(*args, **kwargs)

    def can_view(self, *args, **kwargs):
        return super(Machine, self).can_view(*args, **kwargs)


class ModelSwitch(AclMixin, RevMixin, models.Model):
    """Un modèle (au sens constructeur) de switch"""

    reference = models.CharField(max_length=255)
    commercial_name = models.CharField(max_length=255, null=True, blank=True)
    constructor = models.ForeignKey(
        "topologie.ConstructorSwitch", on_delete=models.PROTECT
    )
    firmware = models.CharField(max_length=255, null=True, blank=True)
    is_modular = models.BooleanField(
        default=False, help_text=_("The switch model is modular.")
    )
    is_itself_module = models.BooleanField(
        default=False, help_text=_("The switch is considered as a module.")
    )

    class Meta:
        permissions = (("view_modelswitch", _("Can view a switch model object")),)
        verbose_name = _("switch model")
        verbose_name_plural = _("switch models")

    def __str__(self):
        if self.commercial_name:
            return str(self.constructor) + " " + str(self.commercial_name)
        else:
            return str(self.constructor) + " " + self.reference


class ModuleSwitch(AclMixin, RevMixin, models.Model):
    """A module of a switch"""

    reference = models.CharField(
        max_length=255,
        help_text=_("Reference of a module."),
        verbose_name=_("module reference"),
    )
    comment = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Comment."),
        verbose_name=_("comment"),
    )

    class Meta:
        permissions = (("view_moduleswitch", _("Can view a switch module object")),)
        verbose_name = _("switch module")
        verbose_name_plural = _("switch modules")

    def __str__(self):
        return str(self.reference)


class ModuleOnSwitch(AclMixin, RevMixin, models.Model):
    """Link beetween module and switch"""

    module = models.ForeignKey("ModuleSwitch", on_delete=models.CASCADE)
    switch = models.ForeignKey("Switch", on_delete=models.CASCADE)
    slot = models.CharField(
        max_length=15, help_text=_("Slot on switch."), verbose_name=_("slot")
    )

    class Meta:
        permissions = (
            (
                "view_moduleonswitch",
                _("Can view a link between switch and module object"),
            ),
        )
        verbose_name = _("link between switch and module")
        verbose_name_plural = _("links between switch and module")
        unique_together = ["slot", "switch"]

    def __str__(self):
        return _("On slot %(slot)s of %(switch)s").format(
            slot=str(self.slot), switch=str(self.switch)
        )


class ConstructorSwitch(AclMixin, RevMixin, models.Model):
    """Un constructeur de switch"""

    name = models.CharField(max_length=255)

    class Meta:
        permissions = (
            ("view_constructorswitch", _("Can view a switch constructor object")),
        )
        verbose_name = _("switch constructor")
        verbose_name_plural = _("switch constructors")

    def __str__(self):
        return self.name


class SwitchBay(AclMixin, RevMixin, models.Model):
    """Une baie de brassage"""

    name = models.CharField(max_length=255)
    building = models.ForeignKey("Building", on_delete=models.PROTECT)
    info = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        permissions = (("view_switchbay", _("Can view a switch bay object")),)
        verbose_name = _("switch bay")
        verbose_name_plural = _("switch bays")

    def __str__(self):
        return self.name


class Dormitory(AclMixin, RevMixin, models.Model):
    """A student accomodation/dormitory
    Une résidence universitaire"""

    name = models.CharField(max_length=255)

    class Meta:
        permissions = (("view_dormitory", _("Can view a dormitory object")),)
        verbose_name = _("dormitory")
        verbose_name_plural = _("dormitories")

    def all_ap_in(self):
        """Returns all ap of the dorms"""
        return AccessPoint.all_ap_in(self.building_set.all())

    @classmethod
    def is_multiple_dorms(cls):
        multiple_dorms = cache.get("multiple_dorms")
        if multiple_dorms:
            return multiple_dorms
        else:
            return cache.get_or_set("multiple_dorms", cls.objects.count() > 1)

    def __str__(self):
        return self.name


class Building(AclMixin, RevMixin, models.Model):
    """A building of a dormitory
    Un batiment"""

    name = models.CharField(max_length=255)
    dormitory = models.ForeignKey("Dormitory", on_delete=models.PROTECT)

    class Meta:
        permissions = (("view_building", _("Can view a building object")),)
        verbose_name = _("building")
        verbose_name_plural = _("buildings")

    def all_ap_in(self):
        """Returns all ap of the building"""
        return AccessPoint.all_ap_in(self)

    def get_name(self):
        if Dormitory.is_multiple_dorms():
            return self.dormitory.name + " : " + self.name
        else:
            return self.name

    @cached_property
    def cached_name(self):
        return self.get_name()

    def __str__(self):
        return self.cached_name


class Port(AclMixin, RevMixin, models.Model):
    """ Definition d'un port. Relié à un switch(foreign_key),
    un port peut etre relié de manière exclusive à :
    - une chambre (room)
    - une machine (serveur etc) (machine_interface)
    - un autre port (uplink) (related)
    Champs supplémentaires :
    - RADIUS (mode STRICT : connexion sur port uniquement si machine
    d'un adhérent à jour de cotisation et que la chambre est également à
    jour de cotisation
    mode COMMON : vérification uniquement du statut de la machine
    mode NO : accepte toute demande venant du port et place sur le vlan normal
    mode BLOQ : rejet de toute authentification
    - vlan_force : override la politique générale de placement vlan, permet
    de forcer un port sur un vlan particulier. S'additionne à la politique
    RADIUS"""

    switch = models.ForeignKey("Switch", related_name="ports", on_delete=models.CASCADE)
    port = models.PositiveIntegerField()
    room = models.ForeignKey("Room", on_delete=models.PROTECT, blank=True, null=True)
    machine_interface = models.ForeignKey(
        "machines.Interface", on_delete=models.SET_NULL, blank=True, null=True
    )
    related = models.OneToOneField(
        "self", null=True, blank=True, related_name="related_port"
    )
    custom_profile = models.ForeignKey(
        "PortProfile", on_delete=models.PROTECT, blank=True, null=True
    )
    state = models.BooleanField(
        default=True,
        help_text=_("Port state Active."),
        verbose_name=_("port state Active"),
    )
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("switch", "port")
        permissions = (("view_port", _("Can view a port object")),)
        verbose_name = _("port")
        verbose_name_plural = _("ports")

    @cached_property
    def pretty_name(self):
        """More elaborated name for label on switch conf"""
        if self.related:
            return _("Uplink: ") + self.related.switch.short_name
        elif self.machine_interface:
            return _("Machine: ") + str(self.machine_interface.domain)
        elif self.room:
            return _("Room: ") + str(self.room)
        else:
            return _("Unknown")

    @cached_property
    def get_port_profile(self):
        """Return the config profil for this port
        :returns: the profile of self (port)

        If is defined a custom profile, returns it
        elIf a default profile is defined for its dormitory, returns it
        Else, returns the global default profil
        If not exists, create a nothing profile"""

        if self.custom_profile:
            return self.custom_profile
        elif self.related:
            return self.switch.default_uplink_profile
        elif self.machine_interface:
            if hasattr(self.machine_interface.machine, "accesspoint"):
                return self.switch.default_access_point_profile
            else:
                return self.switch.default_asso_machine_profile
        elif self.room:
            return self.switch.default_room_profile
        else:
            return Switch.nothing_profile()

    @classmethod
    def get_instance(cls, portid, *_args, **kwargs):
        return (
            cls.objects.select_related("machine_interface__domain__extension")
            .select_related("machine_interface__machine__switch")
            .select_related("room")
            .select_related("related")
            .prefetch_related("switch__interface_set__domain__extension")
            .get(pk=portid)
        )

    def make_port_related(self):
        """ Synchronise le port distant sur self"""
        related_port = self.related
        related_port.related = self
        related_port.save()

    def clean_port_related(self):
        """ Supprime la relation related sur self"""
        related_port = self.related_port
        related_port.related = None
        related_port.save()

    def clean(self):
        """ Verifie que un seul de chambre, interface_parent et related_port
        est rempli. Verifie que le related n'est pas le port lui-même....
        Verifie que le related n'est pas déjà occupé par une machine ou une
        chambre. Si ce n'est pas le cas, applique la relation related
        Si un port related point vers self, on nettoie la relation
        A priori pas d'autre solution que de faire ça à la main. A priori
        tout cela est dans un bloc transaction, donc pas de problème de
        cohérence"""
        if hasattr(self, "switch"):
            if self.port > self.switch.number:
                raise ValidationError(
                    _("The port can't exist, its number is too great.")
                )
        if (
            self.room
            and self.machine_interface
            or self.room
            and self.related
            or self.machine_interface
            and self.related
        ):
            raise ValidationError(
                _("Room, interface and related port are mutually exclusive.")
            )
        if self.related == self:
            raise ValidationError(_("A port can't be related to itself."))
        if self.related and not self.related.related:
            if self.related.machine_interface or self.related.room:
                raise ValidationError(
                    _(
                        "The related port is already used, please clear it"
                        " before creating the relation."
                    )
                )
            else:
                self.make_port_related()
        elif hasattr(self, "related_port"):
            self.clean_port_related()

    def __str__(self):
        return str(self.switch) + " - " + str(self.port)


class Room(AclMixin, RevMixin, models.Model):
    """Une chambre/local contenant une prise murale"""

    name = models.CharField(max_length=255)
    details = models.CharField(max_length=255, blank=True)
    building = models.ForeignKey("Building", on_delete=models.PROTECT)

    class Meta:
        ordering = ["building__name"]
        permissions = (("view_room", _("Can view a room object")),)
        verbose_name = _("room")
        verbose_name_plural = _("rooms")
        unique_together = ("name", "building")

    def __str__(self):
        return self.building.cached_name + " " + self.name


class PortProfile(AclMixin, RevMixin, models.Model):
    """Contains the information of the ports' configuration for a switch"""

    TYPES = (("NO", "NO"), ("802.1X", "802.1X"), ("MAC-radius", _("MAC-RADIUS")))
    MODES = (("STRICT", "STRICT"), ("COMMON", "COMMON"))
    SPEED = (
        ("10-half", "10-half"),
        ("100-half", "100-half"),
        ("10-full", "10-full"),
        ("100-full", "100-full"),
        ("1000-full", "1000-full"),
        ("auto", "auto"),
        ("auto-10", "auto-10"),
        ("auto-100", "auto-100"),
    )
    PROFIL_DEFAULT = (
        ("room", _("Room")),
        ("access_point", _("Access point")),
        ("uplink", _("Uplink")),
        ("asso_machine", _("Organisation machine")),
        ("nothing", _("Nothing")),
    )
    name = models.CharField(max_length=255, verbose_name=_("name"))
    profil_default = models.CharField(
        max_length=32,
        choices=PROFIL_DEFAULT,
        blank=True,
        null=True,
        verbose_name=_("default profile"),
    )
    on_dormitory = models.ForeignKey(
        "topologie.Dormitory",
        related_name="dormitory_ofprofil",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("profile on dormitory"),
    )
    vlan_untagged = models.ForeignKey(
        "machines.Vlan",
        related_name="vlan_untagged",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("VLAN untagged"),
    )
    vlan_tagged = models.ManyToManyField(
        "machines.Vlan",
        related_name="vlan_tagged",
        blank=True,
        verbose_name=_("VLAN(s) tagged"),
    )
    radius_type = models.CharField(
        max_length=32,
        choices=TYPES,
        help_text=_("Type of RADIUS authentication: inactive, MAC-address or 802.1X."),
        verbose_name=_("RADIUS type"),
    )
    radius_mode = models.CharField(
        max_length=32,
        choices=MODES,
        default="COMMON",
        help_text=_(
            "In case of MAC-authentication: mode COMMON or STRICT on this port."
        ),
        verbose_name=_("RADIUS mode"),
    )
    speed = models.CharField(
        max_length=32, choices=SPEED, default="auto", help_text=_("Port speed limit.")
    )
    mac_limit = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Limit of MAC-address on this port."),
        verbose_name=_("MAC limit"),
    )
    flow_control = models.BooleanField(default=False, help_text=_("Flow control."))
    dhcp_snooping = models.BooleanField(
        default=False,
        help_text=_("Protect against rogue DHCP."),
        verbose_name=_("DHCP snooping"),
    )
    dhcpv6_snooping = models.BooleanField(
        default=False,
        help_text=_("Protect against rogue DHCPv6."),
        verbose_name=_("DHCPv6 snooping"),
    )
    arp_protect = models.BooleanField(
        default=False,
        help_text=_("Check if IP address is DHCP assigned."),
        verbose_name=_("ARP protection"),
    )
    ra_guard = models.BooleanField(
        default=False,
        help_text=_("Protect against rogue RA."),
        verbose_name=_("RA guard"),
    )
    loop_protect = models.BooleanField(
        default=False,
        help_text=_("Protect against loop."),
        verbose_name=_("loop protection"),
    )

    class Meta:
        permissions = (("view_portprofile", _("Can view a port profile object")),)
        verbose_name = _("port profile")
        verbose_name_plural = _("port profiles")
        unique_together = ["on_dormitory", "profil_default"]

    security_parameters_fields = [
        "loop_protect",
        "ra_guard",
        "arp_protect",
        "dhcpv6_snooping",
        "dhcp_snooping",
        "flow_control",
    ]

    @cached_property
    def security_parameters_enabled(self):
        return [
            parameter
            for parameter in self.security_parameters_fields
            if getattr(self, parameter)
        ]

    @cached_property
    def security_parameters_as_str(self):
        return ",".join(self.security_parameters_enabled)

    def clean(self):
        """ Check that there is only one generic profil default"""
        super(PortProfile, self).clean()
        if (
            self.profil_default
            and not self.on_dormitory
            and PortProfile.objects.exclude(id=self.id)
            .filter(profil_default=self.profil_default)
            .exclude(on_dormitory__isnull=False)
            .exists()
        ):
            raise ValidationError(
                {
                    "profil_default": _(
                        "A default profile for all dormitories of that type already exists."
                    )
                }
            )

    def __str__(self):
        return self.name


@receiver(post_save, sender=AccessPoint)
def ap_post_save(**_kwargs):
    """Regeneration des noms des bornes vers le controleur"""
    regen("unifi-ap-names")
    regen("graph_topo")


@receiver(post_delete, sender=AccessPoint)
def ap_post_delete(**_kwargs):
    """Regeneration des noms des bornes vers le controleur"""
    regen("unifi-ap-names")
    regen("graph_topo")


@receiver(post_delete, sender=Stack)
def stack_post_delete(**_kwargs):
    """Vide les id des switches membres d'une stack supprimée"""
    Switch.objects.filter(stack=None).update(stack_member_id=None)


@receiver(post_save, sender=Port)
def port_post_save(**_kwargs):
    regen("graph_topo")


@receiver(post_delete, sender=Port)
def port_post_delete(**_kwargs):
    regen("graph_topo")


@receiver(post_save, sender=ModelSwitch)
def modelswitch_post_save(**_kwargs):
    regen("graph_topo")


@receiver(post_delete, sender=ModelSwitch)
def modelswitch_post_delete(**_kwargs):
    regen("graph_topo")


@receiver(post_save, sender=Building)
def building_post_save(**_kwargs):
    regen("graph_topo")


@receiver(post_delete, sender=Building)
def building_post_delete(**_kwargs):
    regen("graph_topo")


@receiver(post_save, sender=Switch)
def switch_post_save(**_kwargs):
    regen("graph_topo")


@receiver(post_delete, sender=Switch)
def switch_post_delete(**_kwargs):
    regen("graph_topo")
