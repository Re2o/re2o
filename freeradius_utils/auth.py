# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyirght © 2017  Daniel Stan
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
Python backend for freeradius.

This file contains definition of some functions called by freeradius backend
during auth for wifi, wired device and nas.

Other examples can be found here :
https://github.com/FreeRADIUS/freeradius-server/blob/master/src/modules/rlm_python/

Inspired by Daniel Stan in Crans
"""

import logging
import os
import sys
import traceback

import radiusd  # Magic module freeradius (radiusd.py is dummy)
from django.core.wsgi import get_wsgi_application
from django.db.models import Q

proj_path = "/var/www/re2o/"
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re2o.settings")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
application = get_wsgi_application()

from machines.models import Domain, Interface, IpList, Nas
from preferences.models import RadiusOption
from topologie.models import Port, Switch
from users.models import User


# Logging
class RadiusdHandler(logging.Handler):
    """Logs handler for freeradius"""

    def emit(self, record):
        """Log message processing, level are converted"""
        if record.levelno >= logging.WARN:
            rad_sig = radiusd.L_ERR
        elif record.levelno >= logging.INFO:
            rad_sig = radiusd.L_INFO
        else:
            rad_sig = radiusd.L_DBG
        radiusd.radlog(rad_sig, str(record.msg))


# Init for logging
logger = logging.getLogger("auth.py")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s: [%(levelname)s] %(message)s")
handler = RadiusdHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def radius_event(fun):
    """Decorator for freeradius fonction with radius.
    This function take a unique argument which is a list of tuples (key, value)
    and return a tuple of 3 values which are:
     * return code (see radiusd.RLM_MODULE_* )
     * a tuple of 2 elements for response value (access ok , etc)
     * a tuple of 2 elements for internal value to update (password for example)

    Here, we convert the list of tuples into a dictionnary.
    """

    def new_f(auth_data):
        """ The function transforming the tuples as dict """
        if isinstance(auth_data, dict):
            data = auth_data
        else:
            data = dict()
            for (key, value) in auth_data or []:
                # Beware: les valeurs scalaires sont entre guillemets
                # Ex: Calling-Station-Id: "une_adresse_mac"
                data[key] = value.replace('"', "")
        try:
            return fun(data)
        except Exception as err:
            exc_type, exc_instance, exc_traceback = sys.exc_info()
            formatted_traceback = "".join(traceback.format_tb(exc_traceback))
            logger.error("Failed %r on data %r" % (err, auth_data))
            logger.error("Function %r, Traceback : %r" % (fun, formatted_traceback))
            return radiusd.RLM_MODULE_FAIL

    return new_f


@radius_event
def instantiate(*_):
    """Usefull for instantiate ldap connexions otherwise,
    do nothing"""
    logger.info("Instantiation")


@radius_event
def authorize(data):
    """Here, we test if the Nas is known.
    - If the nas is unknown, we assume that it is a 802.1X request,
    - If the nas is known, we apply the 802.1X if enabled,
    - It the nas is known AND nas auth is enabled with mac address, returns
    accept here"""
    # For proxified request, split
    nas = data.get("NAS-IP-Address", data.get("NAS-Identifier", None))
    nas_instance = find_nas_from_request(nas)
    # For none proxified requests
    nas_type = None
    if nas_instance:
        nas_type = Nas.objects.filter(nas_type=nas_instance.machine_type).first()
    if not nas_type or nas_type.port_access_mode == "802.1X":
        user = data.get("User-Name", "")
        user = user.split("@", 1)[0]
        mac = data.get("Calling-Station-Id", "")
        result, log, password = check_user_machine_and_register(nas_type, user, mac)
        logger.info(str(log))
        logger.info(str(user))

        if not result:
            return radiusd.RLM_MODULE_REJECT
        else:
            return (
                radiusd.RLM_MODULE_UPDATED,
                (),
                ((str("NT-Password"), str(password)),),
            )

    else:
        return (radiusd.RLM_MODULE_UPDATED, (), (("Auth-Type", "Accept"),))


@radius_event
def post_auth(data):
    """Function called after the user is authenticated"""

    nas = data.get("NAS-IP-Address", data.get("NAS-Identifier", None))
    nas_instance = find_nas_from_request(nas)
    # All non proxified requests
    if not nas_instance:
        logger.info("Proxified request, nas unknown")
        return radiusd.RLM_MODULE_OK
    nas_type = Nas.objects.filter(nas_type=nas_instance.machine_type).first()
    if not nas_type:
        logger.info("This kind of nas is not registered in the database!")
        return radiusd.RLM_MODULE_OK

    mac = data.get("Calling-Station-Id", None)

    # Switchs and access point can have several interfaces
    nas_machine = nas_instance.machine
    # If it is a switchs
    if hasattr(nas_machine, "switch"):
        port = data.get("NAS-Port-Id", data.get("NAS-Port", None))
        # If the switch is part of a stack, calling ip is different from calling switch.
        instance_stack = nas_machine.switch.stack
        if instance_stack:
            # If it is a stack, we select the correct switch in the stack
            id_stack_member = port.split("-")[1].split("/")[0]
            nas_machine = (
                Switch.objects.filter(stack=instance_stack)
                .filter(stack_member_id=id_stack_member)
                .prefetch_related("interface_set__domain__extension")
                .first()
            )
        # Find the port number from freeradius, works both with HP, Cisco
        # and juniper output
        port = port.split(".")[0].split("/")[-1][-2:]
        out = decide_vlan_switch(nas_machine, nas_type, port, mac)
        sw_name, room, reason, vlan_id, decision, attributes = out

        if decision:
            log_message = "(wired) %s -> %s [%s%s]" % (
                sw_name + ":" + port + "/" + str(room),
                mac,
                vlan_id,
                (reason and ": " + reason),
            )
            logger.info(log_message)

            # Wired connexion
            return (
                radiusd.RLM_MODULE_UPDATED,
                (
                    ("Tunnel-Type", "VLAN"),
                    ("Tunnel-Medium-Type", "IEEE-802"),
                    ("Tunnel-Private-Group-Id", "%d" % int(vlan_id)),
                )
                + tuple(attributes),
                (),
            )
        else:
            log_message = "(fil) %s -> %s [Reject %s]" % (
                sw_name + ":" + port + "/" + str(room),
                mac,
                (reason and ": " + reason),
            )
            logger.info(log_message)

            return (radiusd.RLM_MODULE_REJECT, tuple(attributes), ())

    else:
        return radiusd.RLM_MODULE_OK


# TODO : remove this function
@radius_event
def dummy_fun(_):
    """Do nothing, successfully. """
    return radiusd.RLM_MODULE_OK


def detach(_=None):
    """Detatch the auth"""
    print("*** goodbye from auth.py ***")
    return radiusd.RLM_MODULE_OK


def find_nas_from_request(nas_id):
    """ Get the nas object from its ID """
    nas = (
        Interface.objects.filter(
            Q(domain=Domain.objects.filter(name=nas_id))
            | Q(ipv4=IpList.objects.filter(ipv4=nas_id))
        )
        .select_related("machine_type")
        .select_related("machine__switch__stack")
    )
    return nas.first()


def check_user_machine_and_register(nas_type, username, mac_address):
    """Check if username and mac are registered. Register it if unknown.
    Return the user ntlm password if everything is ok.
    Used for 802.1X auth"""
    interface = Interface.objects.filter(mac_address=mac_address).first()
    user = User.objects.filter(pseudo__iexact=username).first()
    if not user:
        return (False, "User unknown", "")
    if not user.has_access():
        return (False, "Invalid connexion (non-contributing user)", "")
    if interface:
        if interface.machine.user != user:
            return (
                False,
                "Mac address registered on another user account",
                "",
            )
        elif not interface.is_active:
            return (False, "Interface/Machine disabled", "")
        elif not interface.ipv4:
            interface.assign_ipv4()
            return (True, "Ok, new ipv4 assignement...", user.pwd_ntlm)
        else:
            return (True, "Access ok", user.pwd_ntlm)
    elif nas_type:
        if nas_type.autocapture_mac:
            result, reason = user.autoregister_machine(mac_address, nas_type)
            if result:
                return (True, "Access Ok, Registering mac...", user.pwd_ntlm)
            else:
                return (False, "Error during mac register %s" % reason, "")
        else:
            return (False, "Unknown interface/machine", "")
    else:
        return (False, "Unknown interface/machine", "")


def decide_vlan_switch(nas_machine, nas_type, port_number, mac_address):
    """Function for selecting vlan for a switch with wired mac auth radius.
    Several modes are available :
        - all modes:
           - unknown NAS : VLAN_OK,
           - unknown port : Decision set in Re2o RadiusOption
        - No radius on this port : VLAN_OK
        - force : returns vlan provided by the database
        - mode strict:
            - no room : Decision set in Re2o RadiusOption,
            - no user in this room : Reject,
            - user of this room is banned or disable : Reject,
            - user of this room non-contributor and not whitelisted:
            Decision set in Re2o RadiusOption
        - mode common :
            - mac-address already registered:
                - related user non contributor / interface disabled:
                Decision set in Re2o RadiusOption
                - related user is banned:
                Decision set in Re2o RadiusOption
                - user contributing : VLAN_OK (can assign ipv4 if needed)
            - unknown interface :
                - register mac disabled : Decision set in Re2o RadiusOption
                - register mac enabled : redirect to webauth
    Returns:
        tuple with :
            - Switch name (str)
            - Room (str)
            - Reason of the decision (str)
            - vlan_id (int)
            - decision (bool)
            - Other Attributs (attribut:str, operator:str, value:str)
    """
    attributes_kwargs = {
        "client_mac": str(mac_address),
        "switch_port": str(port_number),
    }
    # Get port from switch and port number
    extra_log = ""
    # If NAS is unknown, go to default vlan
    if not nas_machine:
        return (
            "?",
            "Unknown room",
            "Unknown NAS",
            RadiusOption.get_cached_value("vlan_decision_ok").vlan_id,
            True,
            RadiusOption.get_attributes("ok_attributes", attributes_kwargs),
        )

    sw_name = str(getattr(nas_machine, "short_name", str(nas_machine)))

    switch = Switch.objects.filter(machine_ptr=nas_machine).first()
    attributes_kwargs["switch_ip"] = str(switch.ipv4)
    port = Port.objects.filter(switch=switch, port=port_number).first()

    # If the port is unknwon, go to default vlan
    # We don't have enought information to make a better decision
    if not port:
        return (
            sw_name,
            "Unknown port",
            "PUnknown port",
            getattr(
                RadiusOption.get_cached_value("unknown_port_vlan"), "vlan_id", None
            ),
            RadiusOption.get_cached_value("unknown_port") != RadiusOption.REJECT,
            RadiusOption.get_attributes("unknown_port_attributes", attributes_kwargs),
        )

    # Retrieve port profile
    port_profile = port.get_port_profile

    # If a vlan is precised in port config, we use it
    if port_profile.vlan_untagged:
        DECISION_VLAN = int(port_profile.vlan_untagged.vlan_id)
        extra_log = "Force sur vlan " + str(DECISION_VLAN)
        attributes = ()
    else:
        DECISION_VLAN = RadiusOption.get_cached_value("vlan_decision_ok").vlan_id
        attributes = RadiusOption.get_attributes("ok_attributes", attributes_kwargs)

    # If the port is disabled in re2o, REJECT
    if not port.state:
        return (sw_name, port.room, "Port disabled", None, False, ())

    # If radius is disabled, decision is OK
    if port_profile.radius_type == "NO":
        return (
            sw_name,
            "",
            "No Radius auth enabled on this port" + extra_log,
            DECISION_VLAN,
            True,
            attributes,
        )

    # If 802.1X is enabled, people has been previously accepted.
    # Go to the decision vlan
    if (nas_type.port_access_mode, port_profile.radius_type) == ("802.1X", "802.1X"):
        room = port.room or "Room unknown"
        return (
            sw_name,
            room,
            "Accept authentication 802.1X",
            DECISION_VLAN,
            True,
            attributes,
        )

    # Otherwise, we are in mac radius.
    # If strict mode is enabled, we check every user related with this port. If
    # one user or more is not enabled, we reject to prevent from sharing or
    # spoofing mac.
    if port_profile.radius_mode == "STRICT":
        room = port.room
        if not room:
            return (
                sw_name,
                "Unknown",
                "Unkwown room",
                getattr(
                    RadiusOption.get_cached_value("unknown_room_vlan"), "vlan_id", None
                ),
                RadiusOption.get_cached_value("unknown_room") != RadiusOption.REJECT,
                RadiusOption.get_attributes(
                    "unknown_room_attributes", attributes_kwargs
                ),
            )

        room_user = User.objects.filter(
            Q(club__room=port.room) | Q(adherent__room=port.room)
        )
        if not room_user:
            return (
                sw_name,
                room,
                "Non-contributing room",
                getattr(
                    RadiusOption.get_cached_value("non_member_vlan"), "vlan_id", None
                ),
                RadiusOption.get_cached_value("non_member") != RadiusOption.REJECT,
                RadiusOption.get_attributes("non_member_attributes", attributes_kwargs),
            )
        for user in room_user:
            if user.is_ban() or user.state != User.STATE_ACTIVE:
                return (
                    sw_name,
                    room,
                    "User is banned or disabled",
                    getattr(
                        RadiusOption.get_cached_value("banned_vlan"), "vlan_id", None
                    ),
                    RadiusOption.get_cached_value("banned") != RadiusOption.REJECT,
                    RadiusOption.get_attributes("banned_attributes", attributes_kwargs),
                )
            elif user.email_state == User.EMAIL_STATE_UNVERIFIED:
                return (
                    sw_name,
                    room,
                    "User is suspended (mail has not been confirmed)",
                    getattr(
                        RadiusOption.get_cached_value("non_member_vlan"),
                        "vlan_id",
                        None,
                    ),
                    RadiusOption.get_cached_value("non_member") != RadiusOption.REJECT,
                    RadiusOption.get_attributes(
                        "non_member_attributes", attributes_kwargs
                    ),
                )
            elif not (user.is_connected() or user.is_whitelisted()):
                return (
                    sw_name,
                    room,
                    "Non-contributing member",
                    getattr(
                        RadiusOption.get_cached_value("non_member_vlan"),
                        "vlan_id",
                        None,
                    ),
                    RadiusOption.get_cached_value("non_member") != RadiusOption.REJECT,
                    RadiusOption.get_attributes(
                        "non_member_attributes", attributes_kwargs
                    ),
                )
        # else: user OK, so we check MAC now

    # If we are authenticating with mac, we look for the interfaces and its mac address
    if port_profile.radius_mode == "COMMON" or port_profile.radius_mode == "STRICT":
        # Mac auth
        interface = (
            Interface.objects.filter(mac_address=mac_address)
            .select_related("machine__user")
            .select_related("ipv4")
            .first()
        )
        # If mac is unknown,
        if not interface:
            room = port.room
            # We try to register mac, if autocapture is enabled
            # Final decision depend on RADIUSOption set in re2o
            if nas_type.autocapture_mac:
                return (
                    sw_name,
                    room,
                    "Unknown mac/interface",
                    getattr(
                        RadiusOption.get_cached_value("unknown_machine_vlan"),
                        "vlan_id",
                        None,
                    ),
                    RadiusOption.get_cached_value("unknown_machine")
                    != RadiusOption.REJECT,
                    RadiusOption.get_attributes(
                        "unknown_machine_attributes", attributes_kwargs
                    ),
                )
            # Otherwise, if autocapture mac is not enabled,
            else:
                return (
                    sw_name,
                    "",
                    "Unknown mac/interface",
                    getattr(
                        RadiusOption.get_cached_value("unknown_machine_vlan"),
                        "vlan_id",
                        None,
                    ),
                    RadiusOption.get_cached_value("unknown_machine")
                    != RadiusOption.REJECT,
                    RadiusOption.get_attributes(
                        "unknown_machine_attributes", attributes_kwargs
                    ),
                )

        # Mac/Interface is found, check if related user is contributing and ok
        # If needed, set ipv4 to it
        else:
            room = port.room
            if interface.machine.user.is_ban():
                return (
                    sw_name,
                    room,
                    "Banned user",
                    getattr(
                        RadiusOption.get_cached_value("banned_vlan"), "vlan_id", None
                    ),
                    RadiusOption.get_cached_value("banned") != RadiusOption.REJECT,
                    RadiusOption.get_attributes("banned_attributes", attributes_kwargs),
                )
            if not interface.is_active:
                return (
                    sw_name,
                    room,
                    "Disabled interface / non-contributing member",
                    getattr(
                        RadiusOption.get_cached_value("non_member_vlan"),
                        "vlan_id",
                        None,
                    ),
                    RadiusOption.get_cached_value("non_member") != RadiusOption.REJECT,
                    RadiusOption.get_attributes(
                        "non_member_attributes", attributes_kwargs
                    ),
                )
            # If settings is set to related interface vlan policy based on interface type:
            if RadiusOption.get_cached_value("radius_general_policy") == "MACHINE":
                DECISION_VLAN = interface.machine_type.ip_type.vlan.vlan_id
            if not interface.ipv4:
                interface.assign_ipv4()
                return (
                    sw_name,
                    room,
                    "Ok, assigning new ipv4" + extra_log,
                    DECISION_VLAN,
                    True,
                    attributes,
                )
            else:
                return (
                    sw_name,
                    room,
                    "Interface OK" + extra_log,
                    DECISION_VLAN,
                    True,
                    attributes,
                )
