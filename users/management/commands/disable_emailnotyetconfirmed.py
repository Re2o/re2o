# Copyright © 2017-2020  Jean-Romain Garnier
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
    help = "Disable users who haven't confirmed their email."

    def handle(self, *args, **options):
        """First deleting invalid invoices, and then deleting the users"""
        days = OptionalUser.get_cached_value("disable_emailnotyetconfirmed")
        users_to_disable = (
            User.objects.filter(state=User.STATE_EMAIL_NOT_YET_CONFIRMED)
            .filter(email_change_date__lte=timezone.now() - timedelta(days=days))
            .distinct()
        )
        print("Disabling " + str(users_to_disable.count()) + " users.")

        for user in users_to_disable:
            user.state = User.STATE_DISABLED
            user.notif_disable()
            user.save()
