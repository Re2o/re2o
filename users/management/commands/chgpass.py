# ⁻*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Lev-Arcady Sellem
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

import os
import pwd

from django.core.management.base import BaseCommand, CommandError
from users.forms import PassForm
from re2o.script_utils import get_user, get_system_user, form_cli


class Command(BaseCommand):
    help = "Change the password of a user."

    def add_arguments(self, parser):
        parser.add_argument("target_username", nargs="?")

    def handle(self, *args, **kwargs):

        current_username = get_system_user()
        current_user = get_user(current_username)
        target_username = kwargs["target_username"] or current_username
        target_user = get_user(target_username)

        ok, msg = target_user.can_change_password(current_user)
        if not ok:
            raise CommandError(msg)

        self.stdout.write("Password change of %s" % target_user.pseudo)

        form_cli(
            PassForm, current_user, "Password change", instance=target_user
        )
