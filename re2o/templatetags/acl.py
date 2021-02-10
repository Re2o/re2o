# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
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
from django.contrib.contenttypes.models import ContentType
from django.template.base import Node, NodeList

register = template.Library()


def get_model(model_name):
    """Retrieve the model object from its name"""
    splitted = model_name.split(".")
    if len(splitted) > 1:
        try:
            app_label, name = splitted
        except ValueError:
            raise template.TemplateSyntaxError(
                "%r is an inconsistent model name." % model_name
            )
    else:
        app_label, name = None, splitted[0]
    try:
        if app_label is not None:
            content_type = ContentType.objects.get(
                model=name.lower(), app_label=app_label
            )
        else:
            content_type = ContentType.objects.get(model=name.lower())
    except ContentType.DoesNotExist:
        raise template.TemplateSyntaxError(
            "%r is not a valid model for an acl tag." % model_name
        )
    except ContentType.MultipleObjectsReturned:
        raise template.TemplateSyntaxError(
            "More than one model found for %r. Try with `app.model`." % model_name
        )
    return content_type.model_class()


def get_callback(tag_name, obj=None):
    """Return the right function to call back to check for acl"""

    if tag_name == "can_create":
        return acl_fct(obj.can_create, False)
    if tag_name == "cannot_create":
        return acl_fct(obj.can_create, True)
    if tag_name == "can_edit":
        return acl_fct(obj.can_edit, False)
    if tag_name == "cannot_edit":
        return acl_fct(obj.can_edit, True)
    if tag_name == "can_edit_all":
        return acl_fct(obj.can_edit_all, False)
    if tag_name == "cannot_edit_all":
        return acl_fct(obj.can_edit_all, True)
    if tag_name == "can_delete":
        return acl_fct(obj.can_delete, False)
    if tag_name == "cannot_delete":
        return acl_fct(obj.can_delete, True)
    if tag_name == "can_delete_all":
        return acl_fct(obj.can_delete_all, False)
    if tag_name == "cannot_delete_all":
        return acl_fct(obj.can_delete_all, True)
    if tag_name == "can_view":
        return acl_fct(obj.can_view, False)
    if tag_name == "cannot_view":
        return acl_fct(obj.can_view, True)
    if tag_name == "can_view_all":
        return acl_fct(obj.can_view_all, False)
    if tag_name == "cannot_view_all":
        return acl_fct(obj.can_view_all, True)
    if tag_name == "can_list":
        return acl_fct(obj.can_list, False)
    if tag_name == "can_view_app":
        return acl_fct(
            lambda x: (
                not any(not sys.modules[o].can_view(x)[0] for o in obj),
                None,
                None,
            ),
            False,
        )
    if tag_name == "cannot_view_app":
        return acl_fct(
            lambda x: (
                not any(not sys.modules[o].can_view(x)[0] for o in obj),
                None,
                None,
            ),
            True,
        )
    if tag_name == "can_edit_history":
        return acl_fct(
            lambda user: (user.has_perm("admin.change_logentry"), None, None), False
        )
    if tag_name == "cannot_edit_history":
        return acl_fct(
            lambda user: (user.has_perm("admin.change_logentry"), None, None), True
        )
    if tag_name == "can_view_any_app":
        return acl_fct(
            lambda x: (any(sys.modules[o].can_view(x)[0] for o in obj), None, None),
            False,
        )
    if tag_name == "cannot_view_any_app":
        return acl_fct(
            lambda x: (any(sys.modules[o].can_view(x)[0] for o in obj), None, None),
            True,
        )

    raise template.TemplateSyntaxError("%r tag is not a valid can_xxx tag." % tag_name)


def acl_fct(callback, reverse):
    """Build a function to use as an acl checker"""

    def acl_fct_normal(user, *args, **kwargs):
        """The can_xxx checker callback"""
        return callback(user, *args, **kwargs)

    def acl_fct_reverse(user, *args, **kwargs):
        """The cannot_xxx checker callback"""
        can, msg, permissions = callback(user, *args, **kwargs)
        return not can, msg, permissions

    return acl_fct_reverse if reverse else acl_fct_normal


@register.tag("can_edit_history")
@register.tag("cannot_edit_history")
def acl_history_filter(parser, token):
    """Templatetag for acl checking on history."""
    (tag_name,) = token.split_contents()

    callback = get_callback(tag_name)
    oknodes = parser.parse(("acl_else", "acl_end"))
    token = parser.next_token()
    if token.contents == "acl_else":
        konodes = parser.parse(("acl_end"))
        token = parser.next_token()
    else:
        konodes = NodeList()

    assert token.contents == "acl_end"

    return AclNode(tag_name, callback, oknodes, konodes)


@register.tag("can_view_any_app")
@register.tag("cannot_view_any_app")
@register.tag("can_view_app")
@register.tag("cannot_view_app")
def acl_app_filter(parser, token):
    """Templatetag for acl checking on applications."""
    try:
        contents = token.split_contents()
        tag_name = contents[0]
        app_name = contents[1:]
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag require 1 argument: an application" % token.contents.split()[0]
        )
    for name in app_name:
        if name not in sys.modules.keys():
            raise template.TemplateSyntaxError(
                "%r is not a registered application for acl." % name
            )

    callback = get_callback(tag_name, app_name)

    oknodes = parser.parse(("acl_else", "acl_end"))
    token = parser.next_token()
    if token.contents == "acl_else":
        konodes = parser.parse(("acl_end"))
        token = parser.next_token()
    else:
        konodes = NodeList()

    assert token.contents == "acl_end"

    return AclNode(tag_name, callback, oknodes, konodes)


@register.tag("can_change")
@register.tag("cannot_change")
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
            "%r tag require at least 2 argument: the model and the field."
            % token.contents.split()[0]
        )

    model = get_model(model_name)
    callback = getattr(model, "can_change_" + field_name)

    # {% can_create %}
    oknodes = parser.parse(("acl_else", "acl_end"))
    token = parser.next_token()

    # {% can_create_else %}
    if token.contents == "acl_else":
        konodes = parser.parse(("acl_end"))
        token = parser.next_token()
    else:
        konodes = NodeList()

    # {% can_create_end %}
    assert token.contents == "acl_end"

    return AclNode(tag_name, callback, oknodes, konodes, *args)


@register.tag("can_create")
@register.tag("cannot_create")
@register.tag("can_edit_all")
@register.tag("cannot_edit_all")
@register.tag("can_delete_all")
@register.tag("cannot_delete_all")
@register.tag("can_view_all")
@register.tag("cannot_view_all")
@register.tag("can_list")
def acl_model_filter(parser, token):
    """Generic definition of an acl templatetag for acl based on model"""

    try:
        tag_content = token.split_contents()
        tag_name = tag_content[0]
        model_name = tag_content[1]
        args = tag_content[2:]
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag require at least 1 argument: the model." % token.contents.split()[0]
        )

    model = get_model(model_name)
    callback = get_callback(tag_name, model)

    # {% can_create %}
    oknodes = parser.parse(("acl_else", "acl_end"))
    token = parser.next_token()

    # {% can_create_else %}
    if token.contents == "acl_else":
        konodes = parser.parse(("acl_end"))
        token = parser.next_token()
    else:
        konodes = NodeList()

    # {% can_create_end %}
    assert token.contents == "acl_end"

    return AclNode(tag_name, callback, oknodes, konodes, *args)


@register.tag("can_edit")
@register.tag("cannot_edit")
@register.tag("can_delete")
@register.tag("cannot_delete")
@register.tag("can_view")
@register.tag("cannot_view")
def acl_instance_filter(parser, token):
    """Generic definition of an acl templatetag for acl based on instance"""

    try:
        tag_content = token.split_contents()
        tag_name = tag_content[0]
        instance_name = tag_content[1]
        args = tag_content[2:]
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag require at least 1 argument: the instance."
            % token.contents.split()[0]
        )

    # {% can_create %}
    oknodes = parser.parse(("acl_else", "acl_end"))
    token = parser.next_token()

    # {% can_create_else %}
    if token.contents == "acl_else":
        konodes = parser.parse(("acl_end"))
        token = parser.next_token()
    else:
        konodes = NodeList()

    # {% can_create_end %}
    assert token.contents == "acl_end"

    return AclInstanceNode(tag_name, instance_name, oknodes, konodes, *args)


class AclNode(Node):
    """A node for the compiled ACL block when acl callback doesn't require
    context."""

    def __init__(self, tag_name, callback, oknodes, konodes, *args):
        self.tag_name = tag_name
        self.callback = callback
        self.oknodes = oknodes
        self.konodes = konodes
        self.args = [template.Variable(arg) for arg in args]

    def render(self, context):
        resolved_args = [arg.resolve(context) for arg in self.args]
        if context["user"].is_anonymous:
            can = False
        else:
            can, _, _ = self.callback(context["user"], *(resolved_args))
        if can:
            return self.oknodes.render(context)
        return self.konodes.render(context)

    def __repr__(self):
        return "<AclNode %s>" % self.tag_name


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
        if context["user"].is_anonymous:
            can = False
        else:
            can, _, _ = callback(context["user"], *(resolved_args))
        if can:
            return self.oknodes.render(context)
        return self.konodes.render(context)

    def __repr__(self):
        return "<AclInstanceNode %s>" % self.tag_name
