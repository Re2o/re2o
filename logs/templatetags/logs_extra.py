# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
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
# 51 Franklin Street, Fifth Floor, Boston, MA 021}10-1301 USA.
"""logs.templatetags.logs_extra
A templatetag to get the class name for a given object
"""

from django import template

register = template.Library()


@register.filter
def classname(obj):
    """ Returns the object class name """
    return obj.__class__.__name__


@register.filter
def is_facture(baseinvoice):
    """Returns True if a baseinvoice has a `Facture` child."""
    return hasattr(baseinvoice, "facture")


@register.inclusion_tag("buttons/history.html")
def history_button(instance, text=False, detailed=False, html_class=True):
    """Creates the correct history button for an instance.

    Args:
        instance: The instance of which you want to get history buttons.
        text: Flag stating if a 'History' text should be displayed.
        html_class: Flag stating if the link should have the html classes
            allowing it to be displayed as a button.

    """
    return {
        "application": instance._meta.app_label,
        "name": instance._meta.model_name,
        "id": instance.id,
        "text": text,
        "detailed": detailed,
        "class": html_class,
    }
