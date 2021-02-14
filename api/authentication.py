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

"""Defines the authentication classes used in the API to authenticate a user.
"""

import datetime

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class ExpiringTokenAuthentication(TokenAuthentication):
    """Authenticate a user if the provided token is valid and not expired."""

    def authenticate_credentials(self, key):
        """See base class. Add the verification the token is not expired."""
        base = super(ExpiringTokenAuthentication, self)
        user, token = base.authenticate_credentials(key)

        # Check that the genration time of the token is not too old
        token_duration = datetime.timedelta(seconds=settings.API_TOKEN_DURATION)
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        if token.created < utc_now - token_duration:
            raise exceptions.AuthenticationFailed(_("The token has expired."))

        return token.user, token
