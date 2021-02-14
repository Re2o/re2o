# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""re2o.templatetags.self_adhesion
A simple templatagetag which returns the value of the option `self_adhesion`
which indicated if a user can creates an account by himself
"""

from django import template

from preferences.models import OptionalUser

register = template.Library()


@register.simple_tag
def self_adhesion():
    """ Returns True if the user are allowed to create accounts """
    options, _created = OptionalUser.objects.get_or_create()
    return options.self_adhesion
