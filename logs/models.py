# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2020  Jean-Romain Garnier
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
"""logs.models
The models definitions for the logs app
"""
from reversion.models import Version
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group

from machines.models import IpList
from machines.models import Interface
from machines.models import Machine
from machines.models import MachineType
from users.models import User
from users.models import Adherent
from users.models import Club
from topologie.models import Room
from topologie.models import Port


class MachineHistorySearchEvent:
    def __init__(self, user, machine, interface, start=None, end=None):
        """
        :param user: User, The user owning the maching at the time of the event
        :param machine: Version, the machine version related to the interface
        :param interface: Version, the interface targeted by this event
        :param start: datetime, the date at which this version was created
        :param end: datetime, the date at which this version was replace by a new one
        """
        self.user = user
        self.machine = machine
        self.interface = interface
        self.ipv4 = IpList.objects.get(id=interface.field_dict["ipv4_id"]).ipv4
        self.mac = self.interface.field_dict["mac_address"]
        self.start_date = start
        self.end_date = end
        self.comment = interface.revision.get_comment() or None

    def is_similar(self, elt2):
        """
        Checks whether two events are similar enough to be merged
        :return: bool
        """
        return (
            elt2 is not None
            and self.user.id == elt2.user.id
            and self.ipv4 == elt2.ipv4
            and self.machine.field_dict["id"] == elt2.machine.field_dict["id"]
            and self.interface.field_dict["id"] == elt2.interface.field_dict["id"]
        )

    def __repr__(self):
        return "{} ({} - ): from {} to {} ({})".format(
            self.machine,
            self.mac,
            self.ipv4,
            self.start_date,
            self.end_date,
            self.comment or "No comment"
        )


class MachineHistorySearch:
    def __init__(self):
        self.events = []
        self._last_evt = None

    def get(self, search, params):
        """
        :param search: ip or mac to lookup
        :param params: dict built by the search view
        :return: list or None, a list of MachineHistorySearchEvent in reverse chronological order
        """
        self.start = params.get("s", None)
        self.end = params.get("e", None)
        search_type = params.get("t", 0)

        self.events = []
        if search_type == "ip":
            return self._get_by_ip(search)[::-1]
        elif search_type == "mac":
            return self._get_by_mac(search)[::-1]

        return None

    def _add_revision(self, user, machine, interface):
        """
        Add a new revision to the chronological order
        :param user: User, The user owning the maching at the time of the event
        :param machine: Version, the machine version related to the interface
        :param interface: Version, the interface targeted by this event
        """
        evt = MachineHistorySearchEvent(user, machine, interface)
        evt.start_date = interface.revision.date_created

        # Try not to recreate events if it's unnecessary
        if evt.is_similar(self._last_evt):
            return

        # Mark the end of validity of the last element
        if self._last_evt and not self._last_evt.end_date:
            self._last_evt.end_date = evt.start_date

            # If the event ends before the given date, remove it
            if self.start and evt.start_date.date() < self.start:
                self._last_evt = None
                self.events.pop()

        # Make sure the new event starts before the given end date
        if self.end and evt.start_date.date() > self.end:
            return

        # Save the new element
        self.events.append(evt)
        self._last_evt = evt

    def _get_interfaces_for_ip(self, ip):
        """
        :param ip: str
        :return: An iterable object with the Version objects
                 of Interfaces with the given IP
        """
        # TODO: What if ip list was deleted?
        try:
            ip_id = IpList.objects.get(ipv4=ip).id
        except IpList.DoesNotExist:
            return []

        return filter(
            lambda x: x.field_dict["ipv4_id"] == ip_id,
            Version.objects.get_for_model(Interface).order_by("revision__date_created")
        )

    def _get_interfaces_for_mac(self, mac):
        """
        :param mac: str
        :return: An iterable object with the Version objects
                 of Interfaces with the given MAC address
        """
        return filter(
            lambda x: str(x.field_dict["mac_address"]) == mac,
            Version.objects.get_for_model(Interface).order_by("revision__date_created")
        )

    def _get_machines_for_interface(self, interface):
        """
        :param interface: Version, the interface for which to find the machines
        :return: An iterable object with the Version objects of Machine to
                 which the given interface was attributed
        """
        machine_id = interface.field_dict["machine_id"]
        return filter(
            lambda x: x.field_dict["id"] == machine_id,
            Version.objects.get_for_model(Machine).order_by("revision__date_created")
        )

    def _get_user_for_machine(self, machine):
        """
        :param machine: Version, the machine of which the owner must be found
        :return: The user to which the given machine belongs
        """
        # TODO: What if user was deleted?
        user_id = machine.field_dict["user_id"]
        return User.objects.get(id=user_id)

    def _get_by_ip(self, ip):
        """
        :param ip: str, The IP to lookup
        :returns: list, a list of MachineHistorySearchEvent
        """
        interfaces = self._get_interfaces_for_ip(ip)

        for interface in interfaces:
            machines = self._get_machines_for_interface(interface)

            for machine in machines:
                user = self._get_user_for_machine(machine)
                self._add_revision(user, machine, interface)

        return self.events

    def _get_by_mac(self, mac):
        """
        :param mac: str, The MAC address to lookup
        :returns: list, a list of MachineHistorySearchEvent
        """
        interfaces = self._get_interfaces_for_mac(mac)

        for interface in interfaces:
            machines = self._get_machines_for_interface(interface)

            for machine in machines:
                user = self._get_user_for_machine(machine)
                self._add_revision(user, machine, interface)

        return self.events


class RelatedHistory:
    def __init__(self, model_name, object_id, detailed=True):
        """
        :param model_name: Name of the related model (e.g. "user")
        :param object_id: ID of the related object
        :param detailed: Whether the related history should be shown in an detailed view
        """
        self.model_name = model_name
        self.object_id = object_id
        self.detailed = detailed


class HistoryEvent:
    def __init__(self, version, previous_version=None, edited_fields=None):
        """
        :param version: Version, the version of the object for this event
        :param previous_version: Version, the version of the object before this event
        :param edited_fields: list, The list of modified fields by this event
        """
        self.version = version
        self.previous_version = previous_version
        self.edited_fields = edited_fields
        self.date = version.revision.date_created
        self.performed_by = version.revision.user
        self.comment = version.revision.get_comment() or None

    def _repr(self, name, value):
        """
        Returns the best representation of the given field
        :param name: the name of the field
        :param value: the value of the field
        :return: object
        """
        if value is None:
            return _("None")

        return value

    def edits(self, hide=[]):
        """
        Build a list of the changes performed during this event
        :param hide: list, the list of fields for which not to show details
        :return: str
        """
        edits = []

        for field in self.edited_fields:
            if field in hide:
                # Don't show sensitive information
                edits.append((field, None, None))
            else:
                edits.append((
                    field,
                    self._repr(field, self.previous_version.field_dict[field]),
                    self._repr(field, self.version.field_dict[field])
                ))

        return edits


class History:
    def __init__(self):
        self.events = []
        self.related = []  # For example, a machine has a list of its interfaces
        self._last_version = None
        self.event_type = HistoryEvent

    def get(self, instance):
        """
        :param interface: The instance to lookup
        :return: list or None, a list of HistoryEvent, in reverse chronological order
        """
        self.events = []

        # Get all the versions for this interface, with the oldest first
        self._last_version = None
        interface_versions = filter(
            lambda x: x.field_dict["id"] == instance.id,
            Version.objects.get_for_model(type(instance)).order_by("revision__date_created")
        )

        for version in interface_versions:
            self._add_revision(version)

        return self.events[::-1]

    def _compute_diff(self, v1, v2, ignoring=[]):
        """
        Find the edited field between two versions
        :param v1: Version
        :param v2: Version
        :param ignoring: List, a list of fields to ignore
        :return: List of field names
        """
        fields = []

        for key in v1.field_dict.keys():
            if key not in ignoring and v1.field_dict[key] != v2.field_dict[key]:
                fields.append(key)

        return fields

    def _add_revision(self, version):
        """
        Add a new revision to the chronological order
        :param version: Version, The version of the interface for this event
        """
        diff = None
        if self._last_version is not None:
            diff = self._compute_diff(version, self._last_version)

        # Ignore "empty" events
        if not diff:
            self._last_version = version
            return

        evt = self.event_type(version, self._last_version, diff)
        self.events.append(evt)
        self._last_version = version


class UserHistoryEvent(HistoryEvent):
    def __init__(self, user, version, previous_version=None, edited_fields=None):
        """
        :param user: User, The user who's history is being built
        :param version: Version, the version of the user for this event
        :param previous_version: Version, the version of the user before this event
        :param edited_fields: list, The list of modified fields by this event
        """
        super(UserHistoryEvent, self).__init__(version, previous_version, edited_fields)
        self.user = user

    def _repr(self, name, value):
        """
        Returns the best representation of the given field
        :param name: the name of the field
        :param value: the value of the field
        :return: object
        """
        if name == "groups":
            if len(value) == 0:
                # Removed all the user's groups
                return _("None")

            # value is a list of ints
            groups = []
            for gid in value:
                # Try to get the group name, if it's not deleted
                try:
                    groups.append(Group.objects.get(id=gid).name)
                except Group.DoesNotExist:
                    # TODO: Find the group name in the versions?
                    groups.append("{} ({})".format(_("Deleted"), gid))

            return ", ".join(groups)
        elif name == "state":
            if value is not None:
                return User.STATES[value][1]
            else:
                return _("Unknown")
        elif name == "email_state":
            if value is not None:
                return User.EMAIL_STATES[value][1]
            else:
                return _("Unknown")
        elif name == "room_id" and value is not None:
            # Try to get the room name, if it's not deleted
            try:
                return Room.objects.get(id=value)
            except Room.DoesNotExist:
                # TODO: Find the room name in the versions?
                return "{} ({})".format(_("Deleted"), value)
        elif name == "members" or name == "administrators":
            if len(value) == 0:
                # Removed all the club's members
                return _("None")

            # value is a list of ints
            users = []
            for uid in value:
                # Try to get the user's name, if theyr're not deleted
                try:
                    users.append(User.objects.get(id=uid).pseudo)
                except User.DoesNotExist:
                    # TODO: Find the user's name in the versions?
                    users.append("{} ({})".format(_("Deleted"), uid))

            return ", ".join(users)

        return super(UserHistoryEvent, self)._repr(name, value)

    def edits(self, hide=["password", "pwd_ntlm", "gpg_fingerprint"]):
        """
        Build a list of the changes performed during this event
        :param hide: list, the list of fields for which not to show details
        :return: str
        """
        return super(UserHistoryEvent, self).edits(hide)

    def __eq__(self, other):
        return (
            self.user.id == other.user.id
            and self.edited_fields == other.edited_fields
            and self.date == other.date
            and self.performed_by == other.performed_by
            and self.comment == other.comment
        )

    def __hash__(self):
        return hash((self.user.id, frozenset(self.edited_fields), self.date, self.performed_by, self.comment))

    def __repr__(self):
        return "{} edited fields {} of {} ({})".format(
            self.performed_by,
            self.edited_fields or "nothing",
            self.user,
            self.comment or "No comment"
        )


class UserHistory(History):
    def __init__(self):
        super(UserHistory, self).__init__()
        self.event_type = UserHistoryEvent

    def get(self, user):
        """
        :param user: User, the user to lookup
        :return: list or None, a list of UserHistoryEvent, in reverse chronological order
        """
        self.events = []

        # Find whether this is a Club or an Adherent
        try:
            obj = Adherent.objects.get(user_ptr_id=user.id)
        except Adherent.DoesNotExist:
            obj = Club.objects.get(user_ptr_id=user.id)

        # Add as "related" histories the list of Machine objects
        # that were once owned by this user
        self.related = list(filter(
            lambda x: x.field_dict["user_id"] == user.id,
            Version.objects.get_for_model(Machine).order_by("revision__date_created")
        ))
        self.related = sorted(
            list(dict.fromkeys(self.related)),
            key=lambda r: r.model_name
        )

        # Get all the versions for this user, with the oldest first
        self._last_version = None
        user_versions = filter(
            lambda x: x.field_dict["id"] == user.id,
            Version.objects.get_for_model(User).order_by("revision__date_created")
        )

        for version in user_versions:
            self._add_revision(user, version)

        # Do the same thing for the Adherent of Club
        self._last_version = None
        obj_versions = filter(
            lambda x: x.field_dict["id"] == obj.id,
            Version.objects.get_for_model(type(obj)).order_by("revision__date_created")
        )

        for version in obj_versions:
            self._add_revision(user, version)

        # Remove duplicates and sort
        self.events = list(dict.fromkeys(self.events))
        return sorted(
            self.events,
            key=lambda e: e.date,
            reverse=True
        )

    def _add_revision(self, user, version):
        """
        Add a new revision to the chronological order
        :param user: User, The user displayed in this history
        :param version: Version, The version of the user for this event
        """
        diff = None
        if self._last_version is not None:
            diff = self._compute_diff(
                version,
                self._last_version,
                ignoring=["last_login", "pwd_ntlm", "email_change_date"]
            )

        # Ignore "empty" events like login
        if not diff:
            self._last_version = version
            return

        evt = UserHistoryEvent(user, version, self._last_version, diff)
        self.events.append(evt)
        self._last_version = version


class MachineHistoryEvent(HistoryEvent):
    def _repr(self, name, value):
        """
        Returns the best representation of the given field
        :param name: the name of the field
        :param value: the value of the field
        :return: object
        """
        if name == "user_id":
            try:
                return User.objects.get(id=value).pseudo
            except User.DoesNotExist:
                return "{} ({})".format(_("Deleted"), value)

        return super(MachineHistoryEvent, self)._repr(name, value)


class MachineHistory(History):
    def __init__(self):
        super(MachineHistory, self).__init__()
        self.event_type = MachineHistoryEvent

    def get(self, machine):
        super(MachineHistory, self).get(machine)

        # Add as "related" histories the list of Interface objects
        # that were once assigned to this machine
        self.related = list(filter(
            lambda x: x.field_dict["machine_id"] == machine.id,
            Version.objects.get_for_model(Interface).order_by("revision__date_created")
        ))

        # Remove duplicates and sort
        self.related = sorted(
            list(dict.fromkeys(self.related)),
            key=lambda r: r.model_name
        )


class InterfaceHistoryEvent(HistoryEvent):
    def _repr(self, name, value):
        """
        Returns the best representation of the given field
        :param name: the name of the field
        :param value: the value of the field
        :return: object
        """
        if name == "ipv4_id" and value is not None:
            try:
                return IpList.objects.get(id=value)
            except IpList.DoesNotExist:
                return "{} ({})".format(_("Deleted"), value)
        elif name == "machine_type_id":
            try:
                return MachineType.objects.get(id=value).name
            except MachineType.DoesNotExist:
                return "{} ({})".format(_("Deleted"), value)
        elif name == "machine_id":
            try:
                return Machine.objects.get(id=value).get_name() or _("No name")
            except Machine.DoesNotExist:
                return "{} ({})".format(_("Deleted"), value)
        elif name == "port_lists":
            if len(value) == 0:
                return _("None")

            ports = []
            for pid in value:
                try:
                    ports.append(Port.objects.get(id=pid).pretty_name())
                except Group.DoesNotExist:
                    ports.append("{} ({})".format(_("Deleted"), pid))

        return super(InterfaceHistoryEvent, self)._repr(name, value)


class InterfaceHistory(History):
    def __init__(self):
        super(InterfaceHistory, self).__init__()
        self.event_type = InterfaceHistoryEvent
