# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
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

urls_view = [
    # (r"radius/nas-interface-from-id/(?P<nas_id>.+)$", views.nas_from_id_view),
    # (r"radius/nas-from-machine-type/(?P<machine_type>.+)$", views.NasFromMachineTypeView),
    # (r"radius/user-from-username/(?P<username>.+)$", views.UserFromUsernameView),
    # (r"radius/interface-from-mac-address/(?P<mac_address>.+)$", views.InterfaceFromMacAddressView),
]
urls_functional_view = [
    (r"radius/authorize/(?P<nas_id>[^/]+)/(?P<username>.+)/(?P<mac_address>[0-9a-fA-F:\-]{17})$",
     views.authorize, None),
    (r"radius/post_auth/(?P<nas_id>[^/]+)/(?P<nas_port>.+)/(?P<user_mac>[0-9a-fA-F:\-]{17})$",
     views.post_auth, None),
]
