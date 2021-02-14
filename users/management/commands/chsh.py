# ⁻*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Jean-Baptiste Daval
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
import sys

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from reversion import revisions as reversion

from re2o.script_utils import get_system_user, get_user
from users.models import ListShell, User


class Command(BaseCommand):
    help = "Change the default shell of a user."

    def add_arguments(self, parser):
        parser.add_argument("target_username", nargs="?")

    def handle(self, *args, **options):

        current_username = get_system_user()
        current_user = get_user(current_username)

        target_username = options["target_username"] or current_username
        target_user = get_user(target_username)

        # L'utilisateur n'a pas le droit de changer le shell
        ok, msg = target_user.can_change_shell(current_user)
        if not ok:
            raise CommandError(msg)

        shells = ListShell.objects.all()

        current_shell = "unknown"
        if target_user.shell:
            current_shell = target_user.shell.get_pretty_name()
        self.stdout.write(
            "Choose a shell for the user %s (the current shell is"
            " %s):" % (target_user.pseudo, current_shell)
        )
        for shell in shells:
            self.stdout.write(
                "%d - %s (%s)" % (shell.id, shell.get_pretty_name(), shell.shell)
            )
        shell_id = input("Enter a number: ")

        try:
            shell_id = int(shell_id)
        except:
            raise CommandError("Invalid choice.")

        shell = ListShell.objects.filter(id=shell_id)
        if not shell:
            raise CommandError("Invalid choice.")

        target_user.shell = shell.first()
        with transaction.atomic(), reversion.create_revision():
            target_user.save()
            reversion.set_user(current_user)
            reversion.set_comment("Shell changed.")

        self.stdout.write(
            self.style.SUCCESS(
                "Shell changed. The change may take a few minutes to apply."
            )
        )
