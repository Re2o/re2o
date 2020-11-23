# -*- mode: python; coding: utf-8 -*-
# re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
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

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(needs_autoescape=False)
def tick(valeur, autoescape=False):

    if isinstance(valeur, bool):
        if valeur == True:
            result = '<i style="color: #1ECA18;" class="fa fa-check"></i>'
        else:
            result = '<i style="color: #D10115;" class="fa fa-times"></i>'
        return mark_safe(result)

    else:  #  if the value is not a boolean, display it as if tick was not called
        return valeur
