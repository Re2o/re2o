# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyirght © 2017  Daniel Stan
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2020  Corentin Canebier
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

from configparser import ConfigParser

from re2oapi import Re2oAPIClient

import sys
import os
import subprocess
import logging
import traceback
import radiusd
from requests import HTTPError
import urllib.parse


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
            # TODO s'assurer ici que les tuples renvoy  s sont bien des
            # (str,str) : rlm_python ne dig  re PAS les unicodes
            return fun(data)
        except Exception as err:
            exc_type, exc_instance, exc_traceback = sys.exc_info()
            formatted_traceback = "".join(traceback.format_tb(exc_traceback))
            logger.error("Failed %r on data %r" % (err, auth_data))
            logger.error("Function %r, Traceback : %r" %
                         (fun, formatted_traceback))
            return radiusd.RLM_MODULE_FAIL

    return new_f


@radius_event
def instantiate(*_):
    """Instantiate api connection
    """
    logger.info("Instantiation")

    path = (os.path.dirname(os.path.abspath(__file__)))

    config = ConfigParser()
    config.read(path+'/config.ini')

    api_hostname = config.get('Re2o', 'hostname')
    api_password = config.get('Re2o', 'password')
    api_username = config.get('Re2o', 'username')

    global api_client
    api_client = Re2oAPIClient(
        api_hostname, api_username, api_password, use_tls=True)


@radius_event
def authorize(data):
    """Here, we test if the Nas is known.
    - If the nas is unknown, we assume that it is a 802.1X request,
    - If the nas is known, we apply the 802.1X if enabled,
    - It the nas is known AND nas auth is enabled with mac address, returns accept here
    """

    nas = data.get("NAS-IP-Address", data.get("NAS-Identifier", None))
    username = data.get("User-Name", "")
    # For proxified request, split
    username = username.split("@", 1)[0]
    mac = data.get("Calling-Station-Id", "")

    # Get all required objects from API
    data_from_api = api_client.view(
        "radius/authorize/{0}/{1}/{2}".format(
            urllib.parse.quote(nas or "None", safe=""),
            urllib.parse.quote(username or "None", safe=""),
            urllib.parse.quote(mac or "None", safe="")
        ))

    nas_type = data_from_api["nas"]
    user = data_from_api["user"]
    user_interface = data_from_api["user_interface"]

    if not nas_type or nas_type and nas_type["port_access_mode"] == "802.1X":
        result, log, password = check_user_machine_and_register(
            nas_type, user, user_interface, nas, username, mac)
        logger.info(log.encode("utf-8"))
        logger.info(username.encode("utf-8"))

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
    """ Function called after the user is authenticated
    """

    nas = data.get("NAS-IP-Address", data.get("NAS-Identifier", None))
    nas_port = data.get("NAS-Port-Id", data.get("NAS-Port", None))
    mac = data.get("Calling-Station-Id", None)

    # Get all required objects from API
    data_from_api = api_client.view(
        "radius/post_auth/{0}/{1}/{2}".format(
            urllib.parse.quote(nas or "None", safe=""),
            urllib.parse.quote(nas_port or "None", safe=""),
            urllib.parse.quote(mac or "None", safe="")
        ))

    nas_type = data_from_api["nas"]
    port = data_from_api["port"]
    switch = data_from_api["switch"]

    # If proxified request
    if not nas_type:
        logger.info("Proxified request, nas unknown")
        return radiusd.RLM_MODULE_OK

    # If the request is from a switch (wired connection)
    if switch:
        # For logging
        sw_name = switch["name"] or "?"
        room = port["room"] or "Unknown room" if port else "Unknown port"

        out = decide_vlan_switch(data_from_api, mac, nas_port)
        reason, vlan_id, decision, attributes = out

        if decision:
            log_message = "(wired) %s -> %s [%s%s]" % (
                sw_name + ":" + nas_port + "/" + str(room),
                mac,
                vlan_id,
                (reason and ": " + reason),
            )
            logger.info(log_message)

            # Apply vlan from decide_vlan_switch
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
            log_message = "(wired) %s -> %s [Reject %s]" % (
                sw_name + ":" + nas_port + "/" + str(room),
                mac,
                (reason and ": " + reason),
            )
            logger.info(log_message)

            return (radiusd.RLM_MODULE_REJECT, tuple(attributes), ())

    # Else it is from wifi
    else:
        return radiusd.RLM_MODULE_OK


def check_user_machine_and_register(nas_type, user, user_interface, nas_id, username, mac_address):
    """Check if username and mac are registered. Register it if unknown.
    Return the user ntlm password if everything is ok.
    Used for 802.1X auth
    """

    if not user:
        # No username provided
        return (False, "User unknown", "")

    if not user["access"]:
        return (False, "Invalid connexion (non-contributing user)", "")

    if user_interface:
        if user_interface["user_pk"] != user["pk"]:
            return (
                False,
                "Mac address registered on another user account",
                "",
            )

        elif not user_interface["active"]:
            return (False, "Interface/Machine disabled", "")

        elif not user_interface["ipv4"]:
            # Try to autoassign ip
            try:
                api_client.view(
                    "radius/assign_ip/{0}".format(
                        urllib.parse.quote(mac_address or "None", safe="")
                    ))
                return (True, "Ok, new ipv4 assignement...", user.get("pwd_ntlm", ""))
            except HTTPError as err:
                return (False, "Error during ip assignement %s" % err.response.text, "")
        else:
            return (True, "Access ok", user.get("pwd_ntlm", ""))

    elif nas_type:
        # The interface is not yet registred, try to autoregister if enabled
        if nas_type["autocapture_mac"]:
            try:
                api_client.view(
                    "radius/autoregister/{0}/{1}/{2}".format(
                        urllib.parse.quote(nas_id or "None", safe=""),
                        urllib.parse.quote(username or "None", safe=""),
                        urllib.parse.quote(mac_address or "None", safe="")
                    ))
                return (True, "Access Ok, Registering mac...", user["pwd_ntlm"])
            except HTTPError as err:
                return (False, "Error during mac register %s" % err.response.text, "")
            return (False, "Autoregistering is disabled", "")
        else:
            return (False, "Unknown interface/machine", "")
    else:
        return (False, "Unknown interface/machine", "")


def set_radius_attributes_values(attributes, values):
    """Set values of parameters in radius attributes"""
    return (
        (str(attribute["attribute"]), str(attribute["value"] % values))
        for attribute in attributes
    )


def decide_vlan_switch(data_from_api, user_mac, nas_port):
    """Function for selecting vlan for a switch with wired mac auth radius.
    Two modes exist : in strict mode, a registered user cannot connect with
    their machines in a non-registered user room
    Sequentially :
        - all modes:
            - unknown NAS : VLAN_OK,
            - unknown port : Decision set in Re2o RadiusOption
            - No radius on this port : VLAN_OK
            - force : replace VLAN_OK with vlan provided by the database
        - mode strict:
            - no room : Decision set in Re2o RadiusOption,
            - no user in this room : Reject,
            - user of this room is banned or disable : Reject,
            - user of this room non-contributor and not whitelisted: 
                Decision set in Re2o RadiusOption
        - all modes :
            - mac-address already registered:
                - related user non contributor / interface disabled:
                    Decision set in Re2o RadiusOption
                - related user is banned:
                    Decision set in Re2o RadiusOption
                - user contributing : VLAN_OK (can assign ipv4 if needed)
            - unknown interface :
                - register mac disabled : Decision set in Re2o RadiusOption
                - register mac enabled : redirect to webauth (not implemented)
    Returns:
        tuple with :
            - Reason of the decision (str)
            - vlan_id (int)
            - decision (bool)
            - Other Attributs (attribut:str, value:str)
    """

    # Get values from api
    nas_type = data_from_api["nas"]
    room_users = data_from_api["room_users"]
    port = data_from_api["port"]
    port_profile = data_from_api["port_profile"]
    switch = data_from_api["switch"]
    user_interface = data_from_api["user_interface"]
    radius_option = data_from_api["radius_option"]
    EMAIL_STATE_UNVERIFIED = data_from_api["EMAIL_STATE_UNVERIFIED"]
    RADIUS_OPTION_REJECT = data_from_api["RADIUS_OPTION_REJECT"]
    USER_STATE_ACTIVE = data_from_api["USER_STATE_ACTIVE"]

    # Values which can be used as parameters in radius attributes
    attributes_kwargs = {
        "client_mac": str(user_mac),
        # magic split
        "switch_port": str(nas_port.split(".")[0].split("/")[-1][-2:]),
        "switch_ip": str(switch["ipv4"])
    }

    extra_log = ""

    # If the port is unknown, do as in RadiusOption
    if not port or not port_profile:
        return (
            "Unknown port",
            radius_option["unknown_port_vlan"] and radius_option["unknown_port_vlan"]["vlan_id"] or None,
            radius_option["unknown_port"] != RADIUS_OPTION_REJECT,
            set_radius_attributes_values(
                radius_option["unknown_port_attributes"], attributes_kwargs),
        )

    # If a vlan is precised in port config, we use it in place of VLAN_OK
    if port_profile["vlan_untagged"]:
        DECISION_VLAN = int(port_profile["vlan_untagged"]["vlan_id"])
        extra_log = "Force sur vlan %s" % str(DECISION_VLAN)
        attributes = ()
    else:
        DECISION_VLAN = radius_option["vlan_decision_ok"]["vlan_id"]
        attributes = set_radius_attributes_values(
            radius_option["ok_attributes"], attributes_kwargs)

    # If the port is disabled in re2o, REJECT
    if not port["state"]:
        return ("Port disabled", None, False, ())

    # If radius is disabled, decision is OK
    if port_profile["radius_type"] == "NO":
        return (
            "No Radius auth enabled on this port" + extra_log,
            DECISION_VLAN,
            True,
            attributes,
        )

    # If 802.1X is enabled, people has been previously accepted.
    # Go to the decision vlan
    if (nas_type["port_access_mode"], port_profile["radius_type"]) == ("802.1X", "802.1X"):
        return (
            "Accept authentication 802.1X",
            DECISION_VLAN,
            True,
            attributes,
        )

    # Otherwise, we are in mac radius.
    # If strict mode is enabled, we check every user related with this port. If
    # all users and clubs are disabled, we reject to prevent from sharing or
    # spoofing mac.
    if port_profile["radius_mode"] == "STRICT":
        if not port["room"]:
            return (
                "Unkwown room",
                radius_option["unknown_room_vlan"] and radius_option["unknown_room_vlan"]["vlan_id"] or None,
                radius_option["unknown_room"] != RADIUS_OPTION_REJECT,
                set_radius_attributes_values(
                    radius_option["unknown_room_attributes"], attributes_kwargs),
            )

        if not room_users:
            return (
                "Non-contributing room",
                radius_option["non_member_vlan"] and radius_option["non_member_vlan"]["vlan_id"] or None,
                radius_option["non_member"] != RADIUS_OPTION_REJECT,
                set_radius_attributes_values(
                    radius_option["non_member_attributes"], attributes_kwargs),
            )

        all_user_ban = True
        at_least_one_active_user = False

        for user in room_users:
            if not user["is_ban"] and user["state"] == USER_STATE_ACTIVE:
                all_user_ban = False
            if user["email_state"] != EMAIL_STATE_UNVERIFIED and (user["is_connected"] or user["is_whitelisted"]):
                at_least_one_active_user = True

        if all_user_ban:
            return (
                "User is banned or disabled",
                radius_option["banned_vlan"] and radius_option["banned_vlan"]["vlan_id"] or None,
                radius_option["banned"] != RADIUS_OPTION_REJECT,
                set_radius_attributes_values(
                    radius_option["banned_attributes"], attributes_kwargs),
            )
        if not at_least_one_active_user:
            return (
                "Non-contributing member or unconfirmed mail",
                radius_option["non_member_vlan"] and radius_option["non_member_vlan"]["vlan_id"] or None,
                radius_option["non_member"] != RADIUS_OPTION_REJECT,
                set_radius_attributes_values(
                    radius_option["non_member_attributes"], attributes_kwargs),
            )
        # else: user OK, so we check MAC now

    # If mac is unknown,
    if not user_interface:
        # We try to register mac, if autocapture is enabled
        # Final decision depend on RADIUSOption set in re2o
        # Something is not implemented here...
        if nas_type["autocapture_mac"]:
            return (
                "Unknown mac/interface",
                radius_option["unknown_machine_vlan"] and radius_option["unknown_machine_vlan"]["vlan_id"] or None,
                radius_option["unknown_machine"] != RADIUS_OPTION_REJECT,
                set_radius_attributes_values(
                    radius_option["unknown_machine_attributes"], attributes_kwargs),
            )
        # Otherwise, if autocapture mac is not enabled,
        else:
            return (
                "Unknown mac/interface",
                radius_option["unknown_machine_vlan"] and radius_option["unknown_machine_vlan"]["vlan_id"] or None,
                radius_option["unknown_machine"] != RADIUS_OPTION_REJECT,
                set_radius_attributes_values(
                    radius_option["unknown_machine_attributes"], attributes_kwargs),
            )

    # Mac/Interface is found, check if related user is contributing and ok
    # If needed, set ipv4 to it
    else:
        if user_interface["is_ban"]:
            return (
                "Banned user",
                radius_option["banned_vlan"] and radius_option["banned_vlan"]["vlan_id"] or None,
                radius_option["banned"] != RADIUS_OPTION_REJECT,
                set_radius_attributes_values(
                    radius_option["banned_attributes"], attributes_kwargs),
            )
        if not user_interface["active"]:
            return (
                "Disabled interface / non-contributing member",
                radius_option["non_member_vlan"] and radius_option["non_member_vlan"]["vlan_id"] or None,
                radius_option["non_member"] != RADIUS_OPTION_REJECT,
                set_radius_attributes_values(
                    radius_option["non_member_attributes"], attributes_kwargs),
            )
        # If settings is set to related interface vlan policy based on interface type:
        if radius_option["radius_general_policy"] == "MACHINE":
            DECISION_VLAN = user_interface["vlan_id"]
        if not user_interface["ipv4"]:
            try:
                api_client.view(
                    "radius/assign_ip/{0}".format(
                        urllib.parse.quote(user_mac or "None", safe="")
                    ))
                return (
                    "Ok, assigning new ipv4" + extra_log,
                    DECISION_VLAN,
                    True,
                    attributes,
                )
            except HTTPError as err:
                return (
                    "Error during ip assignement %s" % err.response.text + extra_log,
                    DECISION_VLAN,
                    True,
                    attributes,
                )

        else:
            return (
                "Interface OK" + extra_log,
                DECISION_VLAN,
                True,
                attributes,
            )
