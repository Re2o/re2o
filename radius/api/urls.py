# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2020 Corentin Canebier
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

from . import views

urls_functional_view = [
    (
        r"radius/authorize/(?P<nas_id>[^/]+)/(?P<username>.+)$",
        views.authorize,
        None,
    ),
    (
        r"radius/post_auth/(?P<nas_id>[^/]+)/(?P<nas_port>.+)/(?P<user_mac>[^/]{17})/(?P<username>.+)$",
        views.post_auth,
        None,
    ),
    (
        r"radius/autoregister/(?P<nas_id>[^/]+)/(?P<username>.+)/(?P<mac_address>[^/]{17})$",
        views.autoregister_machine,
        None,
    ),
    (r"radius/assign_ip/(?P<mac_address>[0-9a-fA-F\:\-]{17})$", views.assign_ip, None),
]
