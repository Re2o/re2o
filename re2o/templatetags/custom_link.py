# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2022 Cyprien de Cerval
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.from django import template
from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def nav_link():
    template = """
    <li>
        <a href="{}">
            <i class="fa {}"></i> {}
        </a>
    </li>
    """
    res = ""
    for link in settings.NAVBAR_LINKS:
        res += template.format(link[0],link[1],link[2])
    return res