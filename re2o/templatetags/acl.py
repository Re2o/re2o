# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Maël Kervella
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
Set of templatags for using acl in templates:
    - can_create
    - cannot_create

**Parameters**:
    model_name - The model_name that needs to be checked for the current user

**Usage**:
    {% <acl_name> model %}
    <template stuff>
    [{% can_else %}
    <template stuff>]
    {% can_end %}

    where <acl_name> is one of the templatetag names available
    (can_xxx or cannot_xxx)

**Example**:
    {% can_create Machine %}
    <p>I'm authorized to create new machines \o/</p>
    {% can_else %}
    <p>Why can't I create a little machine :(</p>
    {% can_end %}

"""

from django import template
from django.template.base import Node, NodeList

import cotisations.models as cotisations
import logs.models as logs
import machines.models as machines
import topologie.models as topologie
import users.models as users

register = template.Library()


def get_model(model_name):
    # cotisations
        # TODO
    # logs
        # TODO
    # machines
    if model_name == 'Machine':
        return machines.Machine
    elif model_name == 'MachineType':
        return machines.MachineType
    elif model_name == 'IpType':
        return machines.IpType
    elif model_name == 'Vlan':
        return machines.Vlan
    elif model_name == 'Nas':
        return machines.Nas
    elif model_name == 'SOA':
        return machines.SOA
    elif model_name == 'Extension':
        return machines.Extension
    elif model_name == 'Mx':
        return machines.Mx
    elif model_name == 'Ns':
        return machines.Ns
    elif model_name == 'Txt':
        return machines.Txt
    elif model_name == 'Srv':
        return machines.Srv
    elif model_name == 'Interface':
        return machines.Interface
    elif model_name == 'Domain':
        return machines.Domain
    elif model_name == 'IpList':
        return machines.IpList
    elif model_name == 'Service':
        return machines.Service
    elif model_name == 'Service_link':
        return machines.Service_link
    elif model_name == 'OuverturePortList':
        return machines.OuverturePortList
    elif model_name == 'OuverturePort':
        return machines.OuverturePort
    # topologie
        # TODO
    # users
        # TODO
    else:
        raise template.TemplateSyntaxError(
            "%r is not a valid model for %r tag" % model_name, tag_name
        )


def get_callback(tag_name, model_name):
    model = get_model(model_name)

    if tag_name == 'can_create':
        return model.can_create
    if tag_name == 'cannot_create':
        def res(*args, **kwargs):
            can, msg = model.can_create(*args, **kwargs)
            return not can, msg
        return res
    else:
        raise template.TemplateSyntaxError(
            "%r tag is not a valid can_xxx tag" % tag_name
        )


@register.tag('can_create')
@register.tag('cannot_create')
def can_generic(parser, token):

    try:
        tag_name, model_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag require a single argument : the model" % token.contents.split()[0]
        )

    callback = get_callback(tag_name, model_name)

    # {% can_create %}
    oknodes = parser.parse(('can_else', 'can_end'))
    token = parser.next_token()

    # {% can_create_else %}
    if token.contents == 'can_else':
        konodes = parser.parse(('can_end'))
        token = parser.next_token()
    else:
        konodes = NodeList()

    # {% can_create_end %}
    assert token.contents == 'can_end'

    return CanNode( callback, oknodes, konodes )


class CanNode(Node):

    def __init__(self, callback, oknodes, konodes):
        self.callback = callback
        self.oknodes = oknodes
        self.konodes = konodes

    def render(self, context):
        can, _ = self.callback(context['user'])
        if can:
            return self.oknodes.render(context)
        return self.konodes.render(context)
