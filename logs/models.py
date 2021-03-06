# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
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
from reversion.models import Version, Revision
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.db.models import Q
from django.apps import apps
from netaddr import EUI
from macaddress.fields import default_dialect

from machines.models import IpList
from machines.models import Interface
from machines.models import Machine
from machines.models import MachineType
from users.models import User
from users.models import Adherent
from users.models import Club
from topologie.models import Room
from topologie.models import Port

from .forms import classes_for_action_type


def make_version_filter(key, value):
    """
    Builds a filter for a Version object to filter by argument in its
    serialized_date
    :param key: str, The argument's key
    :param value: str or int, The argument's value
    :returns: A Q filter
    """
    # The lookup is done in a json string, so it has to be formated
    # based on the value's type (to add " or not)
    if type(value) is str:
        formatted_value = "\"{}\"".format(value)
    else:
        formatted_value = str(value)

    return (
        Q(serialized_data__contains='\"{}\": {},'.format(key, formatted_value))
        | Q(serialized_data__contains='\"{}\": {}}}'.format(key, formatted_value))
    )


############################
#  Machine history search  #
############################

class MachineHistorySearchEvent:
    def __init__(self, user, machine, interface, start=None, end=None):
        """Initialise an instance of MachineHistorySearchEvent.

        Args:
            user: User, the user owning the machine at the time of the event.
            machine: Version, the machine version related to the interface.
            interface: Version, the interface targeted by this event.
            start: datetime, the date at which this version was created
                (default: None).
            end: datetime, the date at which this version was replace by a new
                one (default: None).
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
        """Check whether two events are similar enough to be merged.

        Args:
            elt2: MachineHistorySearchEvent, the event to compare with self.

        Returns:
            A boolean, True if the events can be merged and False otherwise.
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
        """Get the events in machine histories related to the search.

        Args:
            search: the IP or MAC address used in the search.
            params: the dictionary built by the search view.

        Returns:
            A list of MachineHistorySearchEvent in reverse chronological order.
        """
        self.start = params.get("s", None)
        self.end = params.get("e", None)
        search_type = params.get("t", 0)

        self.events = []
        if search_type == "ip":
            try:
                return self._get_by_ip(search)[::-1]
            except:
                pass
        elif search_type == "mac":
            try:
                search = EUI(search, dialect=default_dialect())
                return self._get_by_mac(search)[::-1]
            except:
                pass

        return []

    def _add_revision(self, user, machine, interface):
        """Add a new revision to the chronological order.

        Args:
            user: User, the user owning the maching at the time of the event.
            machine: Version, the machine version related to the interface.
            interface: Version, the interface targeted by this event.
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
        """Get the Version objects of interfaces with the given IP
        address.

        Args:
            ip: the string corresponding to the IP address.

        Returns:
            An iterable object with the Version objects of interfaces with the
            given IP address.
        """
        # TODO: What if ip list was deleted?
        try:
            ip_id = IpList.objects.get(ipv4=ip).id
        except IpList.DoesNotExist:
            return []

        return (
            Version.objects.get_for_model(Interface)
            .filter(make_version_filter("ipv4", ip_id))
            .order_by("revision__date_created")
        )

    def _get_interfaces_for_mac(self, mac):
        """Get the Version objects of interfaces with the given MAC
        address.

        Args:
            mac: the string corresponding to the MAC address.

        Returns:
            An iterable object with the Version objects of interfaces with the
            given MAC address.
        """
        return (
            Version.objects.get_for_model(Interface)
            .filter(make_version_filter("mac_address", str(mac)))
            .order_by("revision__date_created")
        )

    def _get_machines_for_interface(self, interface):
        """Get the Version objects of machines with the given interface.

        Args:
            interface: Version, the interface used to find machines.

        Returns:
            An iterable object with the Version objects of machines to which
            the given interface was assigned.
        """
        machine_id = interface.field_dict["machine_id"]
        return (
            Version.objects.get_for_model(Machine)
            .filter(make_version_filter("pk", machine_id))
            .order_by("revision__date_created")
        )

    def _get_user_for_machine(self, machine):
        """Get the User instance owning the given machine.

        Args:
            machine: Version, the machine used to find its owner.

        Returns:
            The User instance of the owner of the given machine.
        """
        # TODO: What if user was deleted?
        user_id = machine.field_dict["user_id"]
        return User.objects.get(id=user_id)

    def _get_by_ip(self, ip):
        """Get events related to the given IP address.

        Args:
            ip: the string corresponding to the IP address.

        Returns:
            A list of MachineHistorySearchEvent related to the given IP
            address.
        """
        interfaces = self._get_interfaces_for_ip(ip)

        for interface in interfaces:
            machines = self._get_machines_for_interface(interface)

            for machine in machines:
                user = self._get_user_for_machine(machine)
                self._add_revision(user, machine, interface)

        return self.events

    def _get_by_mac(self, mac):
        """Get events related to the given MAC address.

        Args:
            mac: the string corresponding to the MAC address.

        Returns:
            A list of MachineHistorySearchEvent related to the given MAC
            address.
        """
        interfaces = self._get_interfaces_for_mac(mac)

        for interface in interfaces:
            machines = self._get_machines_for_interface(interface)

            for machine in machines:
                user = self._get_user_for_machine(machine)
                self._add_revision(user, machine, interface)

        return self.events


############################
#  Generic history classes #
############################

class RelatedHistory:
    def __init__(self, version):
        """Initialise an instance of RelatedHistory.

        Args:
            version: Version, the version related to the history.
        """
        self.version = version
        self.app_name = version.content_type.app_label
        self.model_name = version.content_type.model
        self.object_id = version.object_id
        self.name = version.object_repr

        if self.model_name:
            self.name = "{}: {}".format(self.model_name.title(), self.name)

    def __eq__(self, other):
        return (
            self.model_name == other.model_name
            and self.object_id == other.object_id
        )

    def __hash__(self):
        return hash((self.model_name, self.object_id))


class HistoryEvent:
    def __init__(self, version, previous_version=None, edited_fields=None):
        """Initialise an instance of HistoryEvent.

        Args:
            version: Version, the version of the object for this event.
            previous_version: Version, the version of the object before this
                event (default: None).
            edited_fields: list, The list of modified fields by this event
                (default: None).
        """
        self.version = version
        self.previous_version = previous_version
        self.edited_fields = edited_fields or []
        self.date = version.revision.date_created
        self.performed_by = version.revision.user
        self.comment = version.revision.get_comment() or None

    def _repr(self, name, value):
        """Get the appropriate representation of the given field.

        Args:
            name: the name of the field
            value: the value of the field

        Returns:
            The string corresponding to the appropriate representation of the
            given field.
        """
        if value is None:
            return _("None")

        return value

    def edits(self, hide=["password", "pwd_ntlm"]):
        """Get the list of the changes performed during this event.

        Args:
            hide: the list of fields for which not to show details (default:
            []).

        Returns:
            The list of fields edited by the event to display.
        """
        edits = []

        for field in self.edited_fields:
            old_value = None
            new_value = None
            if field in hide:
                # Don't show sensitive information, so leave values at None
                pass
            else:
                # Take into account keys that may exist in only one dict
                if field in self.previous_version.field_dict:
                    old_value = self._repr(
                        field,
                        self.previous_version.field_dict[field]
                    )

                if field in self.version.field_dict:
                    new_value = self._repr(
                        field,
                        self.version.field_dict[field]
                    )

            edits.append((field, old_value, new_value))

        return edits


class History:
    def __init__(self):
        self.name = None
        self.events = []
        self.related = []  # For example, a machine has a list of its interfaces
        self._last_version = None
        self.event_type = HistoryEvent

    def get(self, instance_id, model):
        """Get the list of history events of the given object.

        Args:
            instance_id: int, the id of the instance to lookup.
            model: class, the type of object to lookup.

        Returns:
            A list of HistoryEvent, in reverse chronological order, related to
            the given object or None if no version was found.
        """
        self.events = []

        # Get all the versions for this instance, with the oldest first
        self._last_version = None
        interface_versions = (
            Version.objects.get_for_model(model)
            .filter(make_version_filter("pk", instance_id))
            .order_by("revision__date_created")
        )

        for version in interface_versions:
            self._add_revision(version)

        # Return None if interface_versions was empty
        if self._last_version is None:
            return None

        self.name = self._last_version.object_repr
        return self.events[::-1]

    def _compute_diff(self, v1, v2, ignoring=[]):
        """Find the edited fields between two versions.

        Args:
            v1: Version to compare.
            v2: Version to compare.
            ignoring: a list of fields to ignore.

        Returns:
            The list of field names in v1 that are different from the ones in
            v2.
        """
        fields = []
        v1_keys = set([k for k in v1.field_dict.keys() if k not in ignoring])
        v2_keys = set([k for k in v2.field_dict.keys() if k not in ignoring])

        common_keys = v1_keys.intersection(v2_keys)
        fields += list(v2_keys - v1_keys)
        fields += list(v1_keys - v2_keys)

        for key in common_keys:
            if v1.field_dict[key] != v2.field_dict[key]:
                fields.append(key)

        return fields

    def _add_revision(self, version):
        """Add a new revision to the chronological order.

        Args:
            version: Version, the version of the interface for this event.
        """
        diff = None
        if self._last_version is not None:
            diff = self._compute_diff(version, self._last_version)

        # Ignore "empty" events
        # but always keep the first event
        if not diff and self._last_version:
            self._last_version = version
            return

        evt = self.event_type(version, self._last_version, diff)
        self.events.append(evt)
        self._last_version = version


############################
#     Revision history     #
############################

class VersionAction(HistoryEvent):
    def __init__(self, version):
        self.version = version

    def name(self):
        return self.version._object_cache or self.version.object_repr

    def application(self):
        return self.version.content_type.app_label

    def model_name(self):
        return self.version.content_type.model

    def object_id(self):
        return self.version.object_id

    def object_type(self):
        return apps.get_model(self.application(), self.model_name())

    def edits(self, hide=["password", "pwd_ntlm", "gpg_fingerprint"]):
        """Get the list of the changes performed during this event.

        Args:
            hide: the list of fields for which not to show details (default:
            ["password", "pwd_ntlm", "gpg_fingerprint"]).

        Returns:
            The list of fields edited by the event to display.
        """
        self.previous_version = self._previous_version()

        if self.previous_version is None:
            return None, None, None

        self.edited_fields = self._compute_diff(self.version, self.previous_version)
        return super(VersionAction, self).edits(hide)

    def _previous_version(self):
        """Get the previous version of self.

        Returns:
            The Version corresponding to the previous version of self, or None
            in case of exception.
        """
        model = self.object_type()
        try:
            query = (
                make_version_filter("pk", self.object_id())
                & Q(
                    revision__date_created__lt=self.version.revision.date_created
                )
            )
            return (Version.objects.get_for_model(model)
                    .filter(query)
                    .order_by("-revision__date_created")[0])
        except Exception:
            return None

    def _compute_diff(self, v1, v2, ignoring=["pwd_ntlm"]):
        """Find the edited fields between two versions.

        Args:
            v1: Version to compare.
            v2: Version to compare.
            ignoring: a list of fields to ignore (default: ["pwd_ntlm"]).

        Returns:
            The list of field names in v1 that are different from the ones in
            v2.
        """
        fields = []
        v1_keys = set([k for k in v1.field_dict.keys() if k not in ignoring])
        v2_keys = set([k for k in v2.field_dict.keys() if k not in ignoring])

        common_keys = v1_keys.intersection(v2_keys)
        fields += list(v2_keys - v1_keys)
        fields += list(v1_keys - v2_keys)

        for key in common_keys:
            if v1.field_dict[key] != v2.field_dict[key]:
                fields.append(key)

        return fields


class RevisionAction:
    """A Revision may group multiple Version objects together."""

    def __init__(self, revision):
        self.performed_by = revision.user
        self.revision = revision
        self.versions = [VersionAction(v) for v in revision.version_set.all()]

    def id(self):
        return self.revision.id

    def date_created(self):
        return self.revision.date_created

    def comment(self):
        return self.revision.get_comment()


class ActionsSearch:
    def get(self, params):
        """Get the Revision objects corresponding to the search.

        Args:
            params: dictionary built by the search view.

        Returns:
            The QuerySet of Revision objects corresponding to the search.
        """
        user = params.get("user", None)
        start = params.get("start_date", None)
        end = params.get("end_date", None)
        action_types = params.get("action_type", None)

        query = Q()

        if user:
            query &= Q(user__pseudo=user)

        if start:
            query &= Q(date_created__gte=start)

        if end:
            query &= Q(date_created__lte=end)

        action_models = self.models_for_action_types(action_types)
        if action_models:
            query &= Q(version__content_type__model__in=action_models)

        return (
            Revision.objects.all()
            .filter(query)
            .select_related("user")
            .prefetch_related("version_set__object")
        )

    def models_for_action_types(self, action_types):
        if action_types is None:
            return None

        classes = []
        for action_type in action_types:
            c = classes_for_action_type(action_type)

            # Selecting "all" removes the filter
            if c is None:
                return None

            classes += list(map(str.lower, c))

        return classes


############################
#  Class-specific history  #
############################

class UserHistoryEvent(HistoryEvent):
    def _repr(self, name, value):
        """Get the appropriate representation of the given field.

        Args:
            name: the name of the field
            value: the value of the field

        Returns:
            The string corresponding to the appropriate representation of the
            given field.
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
        """Get the list of the changes performed during this event.

        Args:
            hide: the list of fields for which not to show details (default:
            ["password", "pwd_ntlm", "gpg_fingerprint"]).

        Returns:
            The list of fields edited by the event to display.
        """
        return super(UserHistoryEvent, self).edits(hide)

    def __eq__(self, other):
        return (
            self.edited_fields == other.edited_fields
            and self.date == other.date
            and self.performed_by == other.performed_by
            and self.comment == other.comment
        )

    def __hash__(self):
        return hash((frozenset(self.edited_fields), self.date, self.performed_by, self.comment))

    def __repr__(self):
        return "{} edited fields {} ({})".format(
            self.performed_by,
            self.edited_fields or "nothing",
            self.comment or "No comment"
        )


class UserHistory(History):
    def __init__(self):
        super(UserHistory, self).__init__()
        self.event_type = UserHistoryEvent

    def get(self, user_id, model):
        """Get the the list of UserHistoryEvent related to the object.

        Args:
            user_id: int, the id of the user to lookup.

        Returns:
            The list of UserHistoryEvent, in reverse chronological order,
            related to the object, or None if nothing was found.
        """
        self.events = []

        # Try to find an Adherent object
        # If it exists, its id will be the same as the user's
        adherents = (
            Version.objects.get_for_model(Adherent)
            .filter(make_version_filter("pk", user_id))
        )
        try:
            obj = adherents[0]
            model = Adherent
        except IndexError:
            obj = None

        # Fallback on a Club
        if obj is None:
            clubs = (
                Version.objects.get_for_model(Club)
                .filter(make_version_filter("pk", user_id))
            )

            try:
                obj = clubs[0]
                model = Club
            except IndexError:
                obj = None

        # If nothing was found, abort
        if obj is None:
            return None

        # Add in "related" elements the list of objects
        # that were once owned by this user
        self.related = (
            Version.objects.all()
            .filter(make_version_filter("user", user_id))
            .order_by("content_type__model")
        )
        self.related = [RelatedHistory(v) for v in self.related]
        self.related = list(dict.fromkeys(self.related))

        # Get all the versions for this user, with the oldest first
        self._last_version = None
        user_versions = (
            Version.objects.get_for_model(User)
            .filter(make_version_filter("pk", user_id))
            .order_by("revision__date_created")
        )

        for version in user_versions:
            self._add_revision(version)

        # Update name
        self.name = self._last_version.field_dict["pseudo"]

        # Do the same thing for the Adherent of Club
        self._last_version = None
        obj_versions = (
            Version.objects.get_for_model(model)
            .filter(make_version_filter("pk", user_id))
            .order_by("revision__date_created")
        )

        for version in obj_versions:
            self._add_revision(version)

        # Remove duplicates and sort
        self.events = list(dict.fromkeys(self.events))
        return sorted(
            self.events,
            key=lambda e: e.date,
            reverse=True
        )

    def _add_revision(self, version):
        """Add a new revision to the chronological order.

        Args:
            version: Version, the version of the user for this event.
        """
        diff = None
        if self._last_version is not None:
            diff = self._compute_diff(
                version,
                self._last_version,
                ignoring=["last_login", "pwd_ntlm", "email_change_date"]
            )

        # Ignore "empty" events like login
        # but always keep the first event
        if not diff and self._last_version:
            self._last_version = version
            return

        evt = UserHistoryEvent(version, self._last_version, diff)
        self.events.append(evt)
        self._last_version = version


class MachineHistoryEvent(HistoryEvent):
    def _repr(self, name, value):
        """Return the appropriate representation of the given field.

        Args:
            name: the name of the field
            value: the value of the field

        Returns:
            The string corresponding to the appropriate representation of the
            given field.
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

    def get(self, machine_id, model):
        """Get the the list of MachineHistoryEvent related to the object.

        Args:
            machine_id: int, the id of the machine to lookup.

        Returns:
            The list of MachineHistoryEvent, in reverse chronological order,
            related to the object.
        """
        self.related = (
            Version.objects.get_for_model(Interface)
            .filter(make_version_filter("machine", machine_id))
            .order_by("content_type__model")
        )

        # Create RelatedHistory objects and remove duplicates
        self.related = [RelatedHistory(v) for v in self.related]
        self.related = list(dict.fromkeys(self.related))

        return super(MachineHistory, self).get(machine_id, Machine)


class InterfaceHistoryEvent(HistoryEvent):
    def _repr(self, name, value):
        """Get the appropriate representation of the given field.

        Args:
            name: the name of the field
            value: the value of the field

        Returns:
            The string corresponding to the appropriate representation of the
            given field.
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

    def get(self, interface_id, model):
        """Get the the list of InterfaceHistoryEvent related to the object.

        Args:
            interface_id: int, the id of the interface to lookup.

        Returns:
            The list of InterfaceHistoryEvent, in reverse chronological order,
            related to the object.
        """
        return super(InterfaceHistory, self).get(interface_id, Interface)


############################
#    History auto-detect   #
############################

HISTORY_CLASS_MAPPING = {
    User: UserHistory,
    Machine: MachineHistory,
    Interface: InterfaceHistory,
    "default": History
}


def get_history_class(model):
    """Get the most appropriate History subclass to represent the given model's
    history.

    Args:
        model: the class for which to get the history.

    Returns:
        The most appropriate History subclass for the given model's history,
        or History if no other was found.
    """
    try:
        return HISTORY_CLASS_MAPPING[model]()
    except KeyError:
        return HISTORY_CLASS_MAPPING["default"]()
