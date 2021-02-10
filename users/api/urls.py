# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018 Maël Kervella
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

urls_viewset = [
    (r"users/user", views.UserViewSet, "user"),
    (r"users/homecreation", views.HomeCreationViewSet, "homecreation"),
    (r"users/normaluser", views.NormalUserViewSet, "normaluser"),
    (r"users/criticaluser", views.CriticalUserViewSet, "criticaluser"),
    (r"users/club", views.ClubViewSet, None),
    (r"users/adherent", views.AdherentViewSet, None),
    (r"users/serviceuser", views.ServiceUserViewSet, None),
    (r"users/school", views.SchoolViewSet, None),
    (r"users/listright", views.ListRightViewSet, None),
    (r"users/shell", views.ShellViewSet, "shell"),
    (r"users/ban", views.BanViewSet, None),
    (r"users/whitelist", views.WhitelistViewSet, None),
    (r"users/emailaddress", views.EMailAddressViewSet, None),
]

urls_view = [
    (r"users/localemail", views.LocalEmailUsersView),
    (r"users/mailing-standard", views.StandardMailingView),
    (r"users/mailing-club", views.ClubMailingView),
    # Deprecated
    (r"localemail/users", views.LocalEmailUsersView),
    (r"mailing/standard", views.StandardMailingView),
    (r"mailing/club", views.ClubMailingView),
]
