# ⁻*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Hugo Levy--Falk
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

import argparse
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import make_aware

from re2o.utils import all_has_access
from users.models import User


def valid_date(s):
    try:
        return make_aware(datetime.datetime.strptime(s, "%d/%m/%Y"))
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


class Command(BaseCommand):
    help = "Allow unactive users archiving by unassigning their IP addresses."

    def add_arguments(self, parser):
        parser.add_argument(
            "--full",
            "-f",
            action="store_true",
            help="Fully archive users, i.e. delete their email address, machines and remove them from the LDAP.",
        )
        parser.add_argument(
            "--date",
            "-d",
            default=datetime.date.today().strftime("%d/%m/%Y"),
            type=valid_date,
            help="Users whose membership ends sooner than this date will be archived.",
        )
        parser.add_argument(
            "--show",
            "-s",
            action="store_true",
            help="Only show a list of users, without doing anything.",
        )
        parser.add_argument(
            "-y",
            action="store_true",
            help="Do not ask for confirmation before fully archiving.",
        )

    def handle(self, *args, **kwargs):
        full_archive = kwargs["full"]
        date = kwargs["date"]
        force = kwargs["y"]
        show = kwargs["show"]

        to_archive_list = (
            User.objects.exclude(id__in=all_has_access())
            .exclude(id__in=all_has_access(search_time=date))
            .exclude(state=User.STATE_NOT_YET_ACTIVE)
            .exclude(state=User.STATE_FULL_ARCHIVE)
            .exclude(state=User.STATE_EMAIL_NOT_YET_CONFIRMED)
        )

        if show:
            self.stdout.write("%s users found : " % to_archive_list.count())
            self.stdout.write("\n".join(map(str, to_archive_list.all())))
            return

        if full_archive and not force:
            self.stdout.write(
                self.style.WARNING(
                    "Please confirm fully archiving (it is a critical operation!) [Y/n]"
                )
            )
            if input() != "Y":
                self.stdout.write("Leaving without archiving.")
                return
        if full_archive:
            self.stdout.write(
                "Fully archiving users with a membership ending prior to %s."
                % date.strftime("%d/%m/%Y")
            )
            User.mass_full_archive(to_archive_list)
        else:
            self.stdout.write(
                "Archiving users with a membership ending prior to %s."
                % date.strftime("%d/%m/%Y")
            )
            to_archive_list = to_archive_list.exclude(state=User.STATE_ARCHIVE)
            User.mass_archive(to_archive_list)
        self.stdout.write(
            self.style.SUCCESS("%s users were archived." % to_archive_list.count())
        )
