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
Set of templatetags for using acl in templates:
    - can_create (model)
    - cannot_create (model)
    - can_edit (instance)
    - cannot_edit (instance)

Some templatetags require a model to calculate the acl while others are need
an instance of a model (either Model.can_xxx or instance.can_xxx)

**Parameters**:
    model_name or instance - Either the model_name (if templatetag is based on
        model) or an instantiated object (if templatetag is base on instance)
        that needs to be checked for the current user
    args - Any other argument that is interpreted as a python object and passed
        to the acl function (can_xxx)

**Usage**:
    {% <acl_name> <obj> [arg1 [arg2 [...]]]%}
    <template stuff>
    [{% acl_else %}
    <template stuff>]
    {% acl_end %}

    where <acl_name> is one of the templatetag names available
    (can_xxx or cannot_xxx)

**Example**:
    {% can_create Machine targeted_user %}
    <p>I'm authorized to create new machines for this guy \\o/</p>
    {% acl_else %}
    <p>Why can't I create a little machine for this guy ? :(</p>
    {% acl_end %}

    {% can_edit user %}
    <p>Oh I can edit myself oO</p>
    {% acl_else %}
    <p>Sniff can't edit my own infos ...</p>
    {% acl_end %}

**How to modify**:
    To add a new acl function (can_xxx or cannot_xxx),
    - if it's based on a model (like can_create), add an entry in
        'get_callback' and register your tag with the other ones juste before
        'acl_model_generic' definition
    - if it's bases on an instance (like can_edit), just register yout tag with
        the other ones juste before 'acl_instance_generic' definition
    To add support for a new model, add an entry in 'get_model' and be sure
    the acl function exists in the model definition

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
    """Retrieve the model object from its name"""

    # cotisations
    # TODO
    # logs
    # TODO
    # machines
    if model_name == 'Machine':
        return machines.Machine
    if model_name == 'MachineType':
        return machines.MachineType
    if model_name == 'IpType':
        return machines.IpType
    if model_name == 'Vlan':
        return machines.Vlan
    if model_name == 'Nas':
        return machines.Nas
    if model_name == 'SOA':
        return machines.SOA
    if model_name == 'Extension':
        return machines.Extension
    if model_name == 'Mx':
        return machines.Mx
    if model_name == 'Ns':
        return machines.Ns
    if model_name == 'Txt':
        return machines.Txt
    if model_name == 'Srv':
        return machines.Srv
    if model_name == 'Interface':
        return machines.Interface
    if model_name == 'Domain':
        return machines.Domain
    if model_name == 'IpList':
        return machines.IpList
    if model_name == 'Service':
        return machines.Service
    if model_name == 'Service_link':
        return machines.Service_link
    if model_name == 'OuverturePortList':
        return machines.OuverturePortList
    if model_name == 'OuverturePort':
        return machines.OuverturePort
    # topologie
        # TODO
    # users
        # TODO
    raise template.TemplateSyntaxError(
        "%r is not a valid model for an acl tag" % model_name
    )


def get_callback(tag_name, obj):
    """Return the right function to call back to check for acl"""

    if tag_name == 'can_create':
        return acl_fct(obj.can_create, False)
    if tag_name == 'cannot_create':
        return acl_fct(obj.can_create, True)
    if tag_name == 'can_edit':
        return acl_fct(obj.can_edit, False)
    if tag_name == 'cannot_edit':
        return acl_fct(obj.can_edit, True)
    raise template.TemplateSyntaxError(
        "%r tag is not a valid can_xxx tag" % tag_name
    )


def acl_fct(callback, reverse):
    """Build a function to use as an acl checker"""

    def acl_fct_normal(user, *args, **kwargs):
        """The can_xxx checker callback"""
        return callback(user, *args, **kwargs)

    def acl_fct_reverse(user, *args, **kwargs):
        """The cannot_xxx checker callback"""
        can, msg = callback(user, *args, **kwargs)
        return not can, msg

    return acl_fct_reverse if reverse else acl_fct_normal


@register.tag('can_create')
@register.tag('cannot_create')
def acl_model_filter(parser, token):
    """Generic definition of an acl templatetag for acl based on model"""

    try:
        tag_content = token.split_contents()
        tag_name = tag_content[0]
        model_name = tag_content[1]
        args = tag_content[2:]
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag require at least 1 argument : the model"
            % token.contents.split()[0]
        )

    model = get_model(model_name)
    callback = get_callback(tag_name, model)

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

    return AclModelNode(callback, oknodes, konodes, *args)


@register.tag('can_edit')
@register.tag('cannot_edit')
def acl_instance_filter(parser, token):
    """Generic definition of an acl templatetag for acl based on instance"""

    try:
        tag_content = token.split_contents()
        tag_name = tag_content[0]
        instance_name = tag_content[1]
        args = tag_content[2:]
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag require at least 1 argument : the instance"
            % token.contents.split()[0]
        )

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

    return AclInstanceNode(tag_name, instance_name, oknodes, konodes, *args)


class AclModelNode(Node):
    """A node for the compiled ACL block when acl is base on model"""

    def __init__(self, callback, oknodes, konodes, *args):
        self.callback = callback
        self.oknodes = oknodes
        self.konodes = konodes
        self.args = [template.Variable(arg) for arg in args]

    def render(self, context):
        resolved_args = [arg.resolve(context) for arg in self.args]
        can, _ = self.callback(context['user'], *(resolved_args))
        if can:
            return self.oknodes.render(context)
        return self.konodes.render(context)


class AclInstanceNode(Node):
    """A node for the compiled ACL block when acl is based on instance"""

    def __init__(self, tag_name, instance_name, oknodes, konodes, *args):
        self.tag_name = tag_name
        self.instance = template.Variable(instance_name)
        self.oknodes = oknodes
        self.konodes = konodes
        self.args = [template.Variable(arg) for arg in args]

    def render(self, context):
        callback = get_callback(self.tag_name, self.instance.resolve(context))
        resolved_args = [arg.resolve(context) for arg in self.args]
        can, _ = callback(context['user'], *(resolved_args))
        if can:
            return self.oknodes.render(context)
        return self.konodes.render(context)
