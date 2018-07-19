# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
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
"""logs.templatetags.logs_extra
A templatetag to get the class name for a given object
"""

from django import template

register = template.Library()


@register.filter
def classname(obj):
    """ Returns the object class name """
    return obj.__class__.__name__


@register.inclusion_tag('buttons/history.html')
def history_button(instance, text=None, html_class=None):
    """Creates the correct history button for an instance."""
    return {
        'application': instance._meta.app_label,
        'name': instance._meta.model_name,
        'id': instance.id,
        'text': text,
        'class': html_class,
    }
