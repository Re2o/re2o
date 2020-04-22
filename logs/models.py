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

from machines.models import IpList
from machines.models import Interface
from machines.models import Machine
from users.models import User


class HistoryEvent:
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


class MachineHistory:
    def __init__(self):
        self.events = []
        self.__last_evt = None

    def get(self, search, params):
        """
        :param search: ip or mac to lookup
        :param params: dict built by the search view
        :return: list or None, a list of HistoryEvent
        """
        self.start = params.get("s", None)
        self.end = params.get("e", None)
        search_type = params.get("t", 0)

        self.events = []
        if search_type == "ip":
            return self.__get_by_ip(search)
        elif search_type == "mac":
            return self.__get_by_mac(search)

        return None

    def __add_revision(self, user, machine, interface):
        """
        Add a new revision to the chronological order
        :param user: User, The user owning the maching at the time of the event
        :param machine: Version, the machine version related to the interface
        :param interface: Version, the interface targeted by this event
        """
        evt = HistoryEvent(user, machine, interface)
        evt.start_date = interface.revision.date_created

        # Try not to recreate events if it's unnecessary
        if evt.is_similar(self.__last_evt):
            return

        # Mark the end of validity of the last element
        if self.__last_evt and not self.__last_evt.end_date:
            self.__last_evt.end_date = evt.start_date

            # If the event ends before the given date, remove it
            if self.start and evt.start_date.date() < self.start:
                self.__last_evt = None
                self.events.pop()

        # Make sure the new event starts before the given end date
        if self.end and evt.start_date.date() > self.end:
            return

        # Save the new element
        self.events.append(evt)
        self.__last_evt = evt

    def __get_interfaces_for_ip(self, ip):
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

    def __get_interfaces_for_mac(self, mac):
        """
        :param mac: str
        :return: An iterable object with the Version objects
                 of Interfaces with the given MAC address
        """
        return filter(
            lambda x: str(x.field_dict["mac_address"]) == mac,
            Version.objects.get_for_model(Interface).order_by("revision__date_created")
        )

    def __get_machines_for_interface(self, interface):
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

    def __get_user_for_machine(self, machine):
        """
        :param machine: Version, the machine of which the owner must be found
        :return: The user to which the given machine belongs
        """
        # TODO: What if user was deleted?
        user_id = machine.field_dict["user_id"]
        return User.objects.get(id=user_id)

    def __get_by_ip(self, ip):
        """
        :param ip: str, The IP to lookup
        :returns: list, a list of HistoryEvent
        """
        interfaces = self.__get_interfaces_for_ip(ip)

        for interface in interfaces:
            machines = self.__get_machines_for_interface(interface)

            for machine in machines:
                user = self.__get_user_for_machine(machine)
                self.__add_revision(user, machine, interface)

        return self.events

    def __get_by_mac(self, mac):
        """
        :param mac: str, The MAC address to lookup
        :returns: list, a list of HistoryEvent
        """
        interfaces = self.__get_interfaces_for_mac(mac)

        for interface in interfaces:
            machines = self.__get_machines_for_interface(interface)

            for machine in machines:
                user = self.__get_user_for_machine(machine)
                self.__add_revision(user, machine, interface)

        return self.events
