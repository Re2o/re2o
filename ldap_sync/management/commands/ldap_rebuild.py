# Copyright © 2018 Maël Kervella
# Copyright © 2021 Hugo Levy-Falk
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
import subprocess
from base64 import decodebytes

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from users.models import User, ListRight, ServiceUser
from ldap_sync.models import synchronise_user, synchronise_serviceuser, synchronise_usergroup


def split_lines(lines):
    """
    Split LDIF lines. They can span over multiple system lines if the
    following system lines begins with a space.
    """
    ret = []
    for line in lines.split(b"\n"):
        if line.startswith(b" ") and len(ret) > 1:
            ret[-1] += line[len(b" ") :]
        else:
            ret.append(line)
    return ret


def flush_ldap(binddn, bindpass, server, usersdn, groupsdn):
    """
    Perform the python (and more understandable) equivalent of the following commands:

    ldapsearch -LLL -s one -D $binddn -w $bindpass -H $server -b $usersdn dn \
            | grep "dn: " | sed -e 's/dn: //g' \
            | ldapdelete -v -D $binddn -w $bindpass -H $server --
    ldapsearch -LLL -s one -D $binddn -w $bindpass -H $server -b $usersdn dn \
            | grep "dn:: " | sed -e 's/dn:: //g' \
            | while read x; do echo "$x" | base64 -d; echo ""; done \
            | ldapdelete -v -D $binddn -w $bindpass -H $server --
    ldapsearch -LLL -s one -D $binddn -w $bindpass -H $server -b $groupsdn dn \
            | grep "dn: " | sed -e 's/dn: //g' \
            | ldapdelete -v -D $binddn -w $bindpass -H $server --
    ldapsearch -LLL -s one -D $binddn -w $bindpass -H $server -b $groupsdn dn \
            | grep "dn:: " | sed -e 's/dn:: //g' \
            | while read x; do echo "$x" | base64 -d; echo ""; done \
            | ldapdelete -v -D $binddn -w $bindpass -H $server --
    """

    to_remove = []

    for lookup in (usersdn, groupsdn):
        search_cmd = [
            "ldapsearch",
            "-LLL",
            "-s",
            "one",
            "-D",
            binddn,
            "-w",
            bindpass,
            "-H",
            server,
            "-b",
            lookup,
            "dn",
        ]
        for line in split_lines(subprocess.check_output(search_cmd)):
            if line.startswith(b"dn: "):
                to_remove.append(line[len(b"dn: ") :])
            elif line.startswith(b"dn:: "):
                # Non ASCII value ares are base64-encoded
                to_remove.append(decodebytes(line[len(b"dn:: ") :]))

    delete_cmd = ["ldapdelete", "-D", binddn, "-w", bindpass, "-H", server] + to_remove
    subprocess.check_call(delete_cmd)


def sync_ldap():
    """Syncrhonize the whole LDAP with the DB."""
    for u in User.objects.all():
        synchronise_user(sender=User, instance=u)
    for lr in ListRight.objects.all():
        synchronise_usergroup(sender=ListRight, instance=lr)
    for s in ServiceUser.objects.all():
        synchronise_serviceuser(sender=ServiceUser, instance=s)


class Command(BaseCommand):
    help = (
        "Destroy the current LDAP data and rebuild it from the DB data."
        " Use with caution."
    )

    def handle(self, *args, **options):

        usersdn = settings.LDAP["base_user_dn"]
        groupsdn = settings.LDAP["base_usergroup_dn"]
        binddn = settings.DATABASES["ldap"]["USER"]
        bindpass = settings.DATABASES["ldap"]["PASSWORD"]
        server = settings.DATABASES["ldap"]["NAME"]

        flush_ldap(binddn, bindpass, server, usersdn, groupsdn)
        self.stdout.write("LDAP emptied.")
        sync_ldap()
        self.stdout.write("LDAP rebuilt.")
