# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
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
from cotisations.models import Facture
from preferences.models import OptionalUser
from datetime import timedelta

from django.utils import timezone


class Command(BaseCommand):
    help = "Delete non members users (not yet active)."

    def handle(self, *args, **options):
        """First deleting invalid invoices, and then deleting the users"""
        days = OptionalUser.get_cached_value("delete_notyetactive")
        users_to_disable = (
            User.objects.filter(state=User.STATE_EMAIL_NOT_YET_CONFIRMED)
            .filter(registered__lte=timezone.now() - timedelta(days=days))
            .distinct()
        )
        print("Disabling " + str(users_to_disable.count()) + " users.")
        
        users_to_disable.delete()
