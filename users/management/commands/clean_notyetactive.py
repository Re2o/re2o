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
from preferences.models import OptionalUser
from datetime import timedelta

from django.utils import timezone

class Command(BaseCommand):
    help = "Delete non members users (not yet active)"

    def handle(self, *args, **options):
        days = OptionalUser.get_cached_value('delete_notyetactive')
        users = User.objects.filter(state=User.STATE_NOT_YET_ACTIVE).filter(registered__lte=timezone.now() - timedelta(days=days))
        print("Deleting " + str(users.count()) + " users")
        users.delete()
