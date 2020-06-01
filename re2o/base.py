# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Gabriel Détraz
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

# -*- coding: utf-8 -*-
"""
Global independant usefull functions
"""

import smtplib

from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from re2o.settings import EMAIL_HOST


# Mapping of srtftime format for better understanding
# https://docs.python.org/3.6/library/datetime.html#strftime-strptime-behavior
datetime_mapping = {
    "%a": "%a",
    "%A": "%A",
    "%w": "%w",
    "%d": "dd",
    "%b": "%b",
    "%B": "%B",
    "%m": "mm",
    "%y": "yy",
    "%Y": "yyyy",
    "%H": "HH",
    "%I": "HH(12h)",
    "%p": "AMPM",
    "%M": "MM",
    "%S": "SS",
    "%f": "µµ",
    "%z": "UTC(+/-HHMM)",
    "%Z": "UTC(TZ)",
    "%j": "%j",
    "%U": "ww",
    "%W": "ww",
    "%c": "%c",
    "%x": "%x",
    "%X": "%X",
    "%%": "%%",
}


def smtp_check(local_part):
    """Return True if the local_part is already taken
       False if available"""
    try:
        srv = smtplib.SMTP(EMAIL_HOST)
        srv.putcmd("vrfy", local_part)
        reply_code = srv.getreply()[0]
        srv.close()
        if reply_code in [250, 252]:
            return True, _("This domain is already taken.")
    except:
        return True, _("SMTP unreachable.")
    return False, None


def convert_datetime_format(format):
    i = 0
    new_format = ""
    while i < len(format):
        if format[i] == "%":
            char = format[i : i + 2]
            new_format += datetime_mapping.get(char, char)
            i += 2
        else:
            new_format += format[i]
            i += 1
    return new_format


def get_input_formats_help_text(input_formats):
    """Returns a help text about the possible input formats"""
    if len(input_formats) > 1:
        help_text_template = _("Format: {main} {more}")
    else:
        help_text_template = _("Format: {main}")
    more_text_template = '<i class="fa fa-question-circle" title="{}"></i>'
    help_text = help_text_template.format(
        main=convert_datetime_format(input_formats[0]),
        more=more_text_template.format(
            "\n".join(map(convert_datetime_format, input_formats))
        ),
    )
    return help_text


class SortTable:
    """ Class gathering uselful stuff to sort the colums of a table, according
    to the column and order requested. It's used with a dict of possible
    values and associated model_fields """

    # All the possible possible values
    # The naming convention is based on the URL or the views function
    # The syntax to describe the sort to apply is a dict where the keys are
    # the url value and the values are a list of model field name to use to
    # order the request. They are applied in the order they are given.
    # A 'default' might be provided to specify what to do if the requested col
    # doesn't match any keys.

    USERS_INDEX = {
        "user_name": ["name"],
        "user_surname": ["surname"],
        "user_pseudo": ["pseudo"],
        "user_room": ["room"],
        "default": ["state", "pseudo"],
    }
    USERS_INDEX_BAN = {
        "ban_user": ["user__pseudo"],
        "ban_start": ["date_start"],
        "ban_end": ["date_end"],
        "default": ["-date_end"],
    }
    USERS_INDEX_WHITE = {
        "white_user": ["user__pseudo"],
        "white_start": ["date_start"],
        "white_end": ["date_end"],
        "default": ["-date_end"],
    }
    USERS_INDEX_SCHOOL = {"school_name": ["name"], "default": ["name"]}
    MACHINES_INDEX = {"machine_name": ["name"], "default": ["pk"]}
    COTISATIONS_INDEX = {
        "cotis_user": ["user__pseudo"],
        "cotis_paiement": ["paiement__moyen"],
        "cotis_date": ["date"],
        "cotis_id": ["id"],
        "default": ["-date"],
    }
    COTISATIONS_CUSTOM = {
        "invoice_date": ["date"],
        "invoice_id": ["id"],
        "invoice_recipient": ["recipient"],
        "invoice_address": ["address"],
        "invoice_payment": ["payment"],
        "default": ["-date"],
    }
    COTISATIONS_CONTROL = {
        "control_name": ["user__adherent__name"],
        "control_surname": ["user__surname"],
        "control_paiement": ["paiement"],
        "control_date": ["date"],
        "control_valid": ["valid"],
        "control_control": ["control"],
        "control_id": ["id"],
        "control_user-id": ["user__id"],
        "default": ["-date"],
    }
    TOPOLOGIE_INDEX = {
        "switch_dns": ["interface__domain__name"],
        "switch_ip": ["interface__ipv4__ipv4"],
        "switch_loc": ["switchbay__name"],
        "switch_ports": ["number"],
        "switch_stack": ["stack__name"],
        "default": ["switchbay", "stack", "stack_member_id"],
    }
    TOPOLOGIE_INDEX_PORT = {
        "port_port": ["port"],
        "port_room": ["room__name"],
        "port_interface": ["machine_interface__domain__name"],
        "port_related": ["related__switch__name"],
        "port_radius": ["radius"],
        "port_vlan": ["vlan_force__name"],
        "default": ["port"],
    }
    TOPOLOGIE_INDEX_ROOM = {
        "room_name": ["name"],
        "building_name": ["building__name"],
        "default": ["building__name", "name"],
    }
    TOPOLOGIE_INDEX_BUILDING = {"building_name": ["name"], "default": ["name"]}
    TOPOLOGIE_INDEX_DORMITORY = {"dormitory_name": ["name"], "default": ["name"]}
    TOPOLOGIE_INDEX_BORNE = {
        "ap_name": ["interface__domain__name"],
        "ap_ip": ["interface__ipv4__ipv4"],
        "ap_mac": ["interface__mac_address"],
        "default": ["interface__domain__name"],
    }
    TOPOLOGIE_INDEX_STACK = {
        "stack_name": ["name"],
        "stack_id": ["stack_id"],
        "default": ["stack_id"],
    }
    TOPOLOGIE_INDEX_MODEL_SWITCH = {
        "model-switch_name": ["reference"],
        "model-switch_contructor": ["constructor__name"],
        "default": ["reference"],
    }
    TOPOLOGIE_INDEX_SWITCH_BAY = {
        "switch-bay_name": ["name"],
        "switch-bay_building": ["building__name"],
        "default": ["name"],
    }
    TOPOLOGIE_INDEX_CONSTRUCTOR_SWITCH = {
        "constructor-switch_name": ["name"],
        "default": ["name"],
    }
    LOGS_INDEX = {
        "sum_date": ["revision__date_created"],
        "default": ["-revision__date_created"],
    }
    LOGS_STATS_LOGS = {
        "logs_author": ["user__name"],
        "logs_date": ["date_created"],
        "default": ["-date_created"],
    }

    @staticmethod
    def sort(request, col, order, values):
        """ Check if the given values are possible and add .order_by() and
        a .reverse() as specified according to those values """
        fields = values.get(col, None)
        if not fields:
            fields = values.get("default", [])
        request = request.order_by(*fields)
        if values.get(col, None) and order == "desc":
            return request.reverse()
        else:
            return request


def re2o_paginator(request, query_set, pagination_number, page_arg="page"):
    """Paginator script for list display in re2o.
    :request:
    :query_set: Query_set to paginate
    :pagination_number: Number of entries to display"""
    paginator = Paginator(query_set, pagination_number)
    page = request.GET.get(page_arg)
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)
    return results
