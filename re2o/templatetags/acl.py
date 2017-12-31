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
    <p>I'm authorized to create new machines.models.for this guy \\o/</p>
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
import sys

from django import template
from django.template.base import Node, NodeList

import cotisations
import machines
import preferences
import topologie
import users

register = template.Library()

MODEL_NAME = {
    # cotisations
    'Facture' : cotisations.models.Facture,
    'Vente' : cotisations.models.Vente,
    'Article' : cotisations.models.Article,
    'Banque' : cotisations.models.Banque,
    'Paiement' : cotisations.models.Paiement,
    'Cotisation' : cotisations.models.Cotisation,
    # machines
    'Machine' : machines.models.Machine,
    'MachineType' : machines.models.MachineType,
    'IpType' : machines.models.IpType,
    'Vlan' : machines.models.Vlan,
    'Nas' : machines.models.Nas,
    'SOA' : machines.models.SOA,
    'Extension' : machines.models.Extension,
    'Mx' : machines.models.Mx,
    'Ns' : machines.models.Ns,
    'Txt' : machines.models.Txt,
    'Srv' : machines.models.Srv,
    'Interface' : machines.models.Interface,
    'Domain' : machines.models.Domain,
    'IpList' : machines.models.IpList,
    'Service' : machines.models.Service,
    'Service_link' : machines.models.Service_link,
    'OuverturePortList' : machines.models.OuverturePortList,
    'OuverturePort' : machines.models.OuverturePort,
    # preferences
    'OptionalUser': preferences.models.OptionalUser,
    'OptionalMachine': preferences.models.OptionalMachine,
    'OptionalTopologie': preferences.models.OptionalTopologie,
    'GeneralOption': preferences.models.GeneralOption,
    'Service': preferences.models.Service,
    'AssoOption': preferences.models.AssoOption,
    'MailMessageOption': preferences.models.MailMessageOption,
    # topologie
    'Stack' : topologie.models.Stack,
    'Switch' : topologie.models.Switch,
    'ModelSwitch' : topologie.models.ModelSwitch,
    'ConstructorSwitch' : topologie.models.ConstructorSwitch,
    'Port' : topologie.models.Port,
    'Room' : topologie.models.Room,
    # users
    'User' : users.models.User,
    'Adherent' : users.models.Adherent,
    'Club' : users.models.Club,
    'ServiceUser' : users.models.ServiceUser,
    'School' : users.models.School,
    'ListRight' : users.models.ListRight,
    'Ban' : users.models.Ban,
    'Whitelist' : users.models.Whitelist,
}


def get_model(model_name):
    """Retrieve the model object from its name"""
    try:
        return MODEL_NAME[model_name]
    except KeyError:
        raise template.TemplateSyntaxError(
            "%r is not a valid model for an acl tag" % model_name
        )


def get_callback(tag_name, obj=None):
    """Return the right function to call back to check for acl"""

    if tag_name == 'can_create':
        return acl_fct(obj.can_create, False)
    if tag_name == 'cannot_create':
        return acl_fct(obj.can_create, True)
    if tag_name == 'can_edit':
        return acl_fct(obj.can_edit, False)
    if tag_name == 'cannot_edit':
        return acl_fct(obj.can_edit, True)
    if tag_name == 'can_edit_all':
        return acl_fct(obj.can_edit_all, False)
    if tag_name == 'cannot_edit_all':
        return acl_fct(obj.can_edit_all, True)
    if tag_name == 'can_delete':
        return acl_fct(obj.can_delete, False)
    if tag_name == 'cannot_delete':
        return acl_fct(obj.can_delete, True)
    if tag_name == 'can_delete_all':
        return acl_fct(obj.can_delete_all, False)
    if tag_name == 'cannot_delete_all':
        return acl_fct(obj.can_delete_all, True)
    if tag_name == 'can_view':
        return acl_fct(obj.can_view, False)
    if tag_name == 'cannot_view':
        return acl_fct(obj.can_view, True)
    if tag_name == 'can_view_all':
        return acl_fct(obj.can_view_all, False)
    if tag_name == 'cannot_view_all':
        return acl_fct(obj.can_view_all, True)
    if tag_name == 'can_view_app':
        return acl_fct(sys.modules[obj].can_view, False)
    if tag_name == 'cannot_view_app':
        return acl_fct(sys.modules[obj].can_view, True)
    if tag_name == 'can_edit_history':
        return acl_fct(lambda user:(user.has_perms(('admin',)),None),False)
    if tag_name == 'cannot_edit_history':
        return acl_fct(lambda user:(user.has_perms(('admin',)),None),True)

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


@register.tag('can_edit_history')
@register.tag('cannot_edit_history')
def acl_history_filter(parser, token):
    """Templatetag for acl checking on history."""
    tag_name, = token.split_contents()

    callback = get_callback(tag_name)
    oknodes = parser.parse(('acl_else', 'acl_end'))
    token = parser.next_token()
    if token.contents == 'acl_else':
        konodes = parser.parse(('acl_end'))
        token = parser.next_token()
    else:
        konodes = NodeList()

    assert token.contents == 'acl_end'

    return AclNode(callback, oknodes, konodes)


@register.tag('can_view_app')
@register.tag('cannot_view_app')
def acl_app_filter(parser, token):
    """Templatetag for acl checking on applications."""
    try:
        tag_name, app_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag require 1 argument : the application"
            % token.contents.split()[0]
        )
    if not app_name in sys.modules.keys():
        raise template.TemplateSyntaxError(
            "%r is not a registered application for acl."
            % app_name
        )

    callback = get_callback(tag_name, app_name)

    oknodes = parser.parse(('acl_else', 'acl_end'))
    token = parser.next_token()
    if token.contents == 'acl_else':
        konodes = parser.parse(('acl_end'))
        token = parser.next_token()
    else:
        konodes = NodeList()

    assert token.contents == 'acl_end'

    return AclNode(callback, oknodes, konodes)

@register.tag('can_change')
@register.tag('cannot_change')
def acl_change_filter(parser, token):
    """Templatetag for acl checking a can_change_xxx function"""

    try:
        tag_content = token.split_contents()
        tag_name = tag_content[0]
        model_name = tag_content[1]
        field_name = tag_content[2]
        args = tag_content[3:]
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag require at least 2 argument : the model and the field"
            % token.contents.split()[0]
        )

    model = get_model(model_name)
    callback = getattr(model, 'can_change_'+field_name)

    # {% can_create %}
    oknodes = parser.parse(('acl_else', 'acl_end'))
    token = parser.next_token()

    # {% can_create_else %}
    if token.contents == 'acl_else':
        konodes = parser.parse(('acl_end'))
        token = parser.next_token()
    else:
        konodes = NodeList()

    # {% can_create_end %}
    assert token.contents == 'acl_end'

    return AclNode(callback, oknodes, konodes, *args)

@register.tag('can_create')
@register.tag('cannot_create')
@register.tag('can_edit_all')
@register.tag('cannot_edit_all')
@register.tag('can_delete_all')
@register.tag('cannot_delete_all')
@register.tag('can_view_all')
@register.tag('cannot_view_all')
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
    oknodes = parser.parse(('acl_else', 'acl_end'))
    token = parser.next_token()

    # {% can_create_else %}
    if token.contents == 'acl_else':
        konodes = parser.parse(('acl_end'))
        token = parser.next_token()
    else:
        konodes = NodeList()

    # {% can_create_end %}
    assert token.contents == 'acl_end'

    return AclNode(callback, oknodes, konodes, *args)


@register.tag('can_edit')
@register.tag('cannot_edit')
@register.tag('can_delete')
@register.tag('cannot_delete')
@register.tag('can_view')
@register.tag('cannot_view')
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
    oknodes = parser.parse(('acl_else', 'acl_end'))
    token = parser.next_token()

    # {% can_create_else %}
    if token.contents == 'acl_else':
        konodes = parser.parse(('acl_end'))
        token = parser.next_token()
    else:
        konodes = NodeList()

    # {% can_create_end %}
    assert token.contents == 'acl_end'

    return AclInstanceNode(tag_name, instance_name, oknodes, konodes, *args)


class AclNode(Node):
    """A node for the compiled ACL block when acl callback doesn't require
    context."""

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
