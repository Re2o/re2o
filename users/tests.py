# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
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
"""users.tests
The tests for the Users module.
"""

import os.path

import volatildap
from django.conf import settings
from django.test import TestCase

from . import models


class SchoolTestCase(TestCase):
    def test_school_are_created(self):
        s = models.School.objects.create(name="My awesome school")
        self.assertEqual(s.name, "My awesome school")


class ListShellTestCase(TestCase):
    def test_shell_are_created(self):
        s = models.ListShell.objects.create(shell="/bin/zsh")
        self.assertEqual(s.shell, "/bin/zsh")


class LdapUserTestCase(TestCase):
    def test_create_ldap_user(self):
        g = models.LdapUser.objects.create(
            gid="500",
            name="users_test_ldapuser",
            uid="users_test_ldapuser",
            uidNumber="21001",
            sn="users_test_ldapuser",
            login_shell="/bin/false",
            mail="user@example.net",
            given_name="users_test_ldapuser",
            home_directory="/home/moamoak",
            display_name="users_test_ldapuser",
            dialupAccess="False",
            sambaSID="21001",
            user_password="{SSHA}aBcDeFgHiJkLmNoPqRsTuVwXyZ012345",
            sambat_nt_password="0123456789ABCDEF0123456789ABCDEF",
            macs=[],
            shadowexpire="0",
        )
        self.assertEqual(g.name, "users_test_ldapuser")


class LdapUserGroupTestCase(TestCase):
    def test_create_ldap_user_group(self):
        g = models.LdapUserGroup.objects.create(
            gid="501", members=[], name="users_test_ldapusergroup"
        )
        self.assertEqual(g.name, "users_test_ldapusergroup")


class LdapServiceUserTestCase(TestCase):
    def test_create_ldap_service_user(self):
        g = models.LdapServiceUser.objects.create(
            name="users_test_ldapserviceuser",
            user_password="{SSHA}AbCdEfGhIjKlMnOpQrStUvWxYz987654",
        )
        self.assertEqual(g.name, "users_test_ldapserviceuser")
