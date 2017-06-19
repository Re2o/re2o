# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
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
#
from django.core.management.base import BaseCommand, CommandError

from users.models import User

class Command(BaseCommand):
    help = 'Synchronise le ldap à partir du sql. A utiliser dans un cron'

    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument(
            '--full',
            action='store_true',
            dest='full',
            default=False,
            help='Régénération complète du ldap (y compris des machines)',
        )

    def handle(self, *args, **options):
        for usr in User.objects.all():
            usr.ldap_sync(mac_refresh=options['full'])

