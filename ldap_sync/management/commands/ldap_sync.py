# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2020  Hugo Levy-Falk
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
#
from django.core.management.base import BaseCommand, CommandError

from ldap_sync.models import synchronise_user
from users.models import User


class Command(BaseCommand):
    help = "Synchronise the LDAP from SQL. To be used in a cron."

    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument(
            "--full",
            action="store_true",
            dest="full",
            default=False,
            help="Complete regeneration of the LDAP (including machines).",
        )

    def handle(self, *args, **options):
        for user in User.objects.all():
            synchronise_user(sender=User, instance=user)
