# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
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
"""users.tests
The tests for the Users module.
"""

from django.test import TestCase
from django.conf import settings
from .models import School, ListShell, LdapUserGroup, ListRight

import volatildap

# Réglages bidon pour volatildap
LdapUserGroup.base_dn='ou=groups,dc=example,dc=org'


groups = ('ou=groups,dc=example,dc=org', {
    'objectClass': ['top', 'organizationalUnit'], 'ou': ['groups']})
people = ('ou=people,dc=example,dc=org', {
    'objectClass': ['top', 'organizationalUnit'], 'ou': ['groups']})
contacts = ('ou=contacts,ou=groups,dc=example,dc=org', {
    'objectClass': ['top', 'organizationalUnit'], 'ou': ['groups']})
foogroup = ('cn=foogroup,ou=groups,dc=example,dc=org', {
    'objectClass': ['posixGroup'], 'memberUid': ['foouser', 'baruser'],
    'gidNumber': ['1000'], 'cn': ['foogroup']})
bargroup = ('cn=bargroup,ou=groups,dc=example,dc=org', {
    'objectClass': ['posixGroup'], 'memberUid': ['zoouser', 'baruser'],
    'gidNumber': ['1001'], 'cn': ['bargroup']})
wizgroup = ('cn=wizgroup,ou=groups,dc=example,dc=org', {
    'objectClass': ['posixGroup'], 'memberUid': ['wizuser', 'baruser'],
    'gidNumber': ['1002'], 'cn': ['wizgroup']})
foouser = ('uid=foouser,ou=people,dc=example,dc=org', {
    'cn': [b'F\xc3\xb4o Us\xc3\xa9r'],
    'objectClass': ['posixAccount', 'shadowAccount', 'inetOrgPerson'],
    'loginShell': ['/bin/bash'],
    'jpegPhoto': [
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff'
        b'\xfe\x00\x1cCreated with GIMP on a Mac\xff\xdb\x00C\x00\x05\x03\x04'
        b'\x04\x04\x03\x05\x04\x04\x04\x05\x05\x05\x06\x07\x0c\x08\x07\x07\x07'
        b'\x07\x0f\x0b\x0b\t\x0c\x11\x0f\x12\x12\x11\x0f\x11\x11\x13\x16\x1c'
        b'\x17\x13\x14\x1a\x15\x11\x11\x18!\x18\x1a\x1d\x1d\x1f\x1f\x1f\x13'
        b'\x17"$"\x1e$\x1c\x1e\x1f\x1e\xff\xdb\x00C\x01\x05\x05\x05\x07\x06\x07'
        b'\x0e\x08\x08\x0e\x1e\x14\x11\x14\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e'
        b'\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e'
        b'\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e'
        b'\x1e\x1e\x1e\x1e\x1e\x1e\x1e\xff\xc0\x00\x11\x08\x00\x08\x00\x08\x03'
        b'\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x15\x00\x01\x01\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00'
        b'\x19\x10\x00\x03\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x01\x02\x06\x11A\xff\xc4\x00\x14\x01\x01\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc4\x00\x14\x11\x01'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff'
        b'\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\x9d\xf29wU5Q\xd6'
        b'\xfd\x00\x01\xff\xd9'],
    'uidNumber': ['2000'], 'gidNumber': ['1000'], 'sn': [b'Us\xc3\xa9r'],
    'homeDirectory': ['/home/foouser'], 'givenName': [b'F\xc3\xb4o'],
    'uid': ['foouser']})

class LdapTestCase(TestCase):
    directory = {}

    @classmethod
    def setUpClass(cls):
        super(LdapTestCase, cls).setUpClass()
        cls.ldap_server = volatildap.LdapServer(
            initial_data=cls.directory,
            schemas=['core.schema', 'cosine.schema', 'inetorgperson.schema', 'nis.schema'],
        )
        settings.DATABASES['ldap']['USER'] = cls.ldap_server.rootdn
        settings.DATABASES['ldap']['PASSWORD'] = cls.ldap_server.rootpw
        settings.DATABASES['ldap']['NAME'] = cls.ldap_server.uri

    @classmethod
    def tearDownClass(cls):
        cls.ldap_server.stop()
        super(LdapTestCase, cls).tearDownClass()

    def setUp(self):
        super(LdapTestCase, self).setUp()
        self.ldap_server.start()


class SchoolTestCase(TestCase):
    def setUp(self):
        School.objects.create(name="ENS Paris-Saclay")
        School.objects.create(name="Supelec")

    def test_school_are_created(self):
        pass

class ListShellTestCase(TestCase):
    def setUp(self):
        ListShell.objects.create(shell="/bin/zsh")
        ListShell.objects.create(shell="/bin/bash")

    def test_shell_are_created(self):
        pass

class GroupTestCase(LdapTestCase):
    directory = dict([groups, foogroup, bargroup, wizgroup, people, foouser])

    def test_create_ldapgroup(self):
        mygroup = LdapUserGroup()
        mygroup.name='re2o'
        mygroup.gid=1010
        mygroup.members=['someuser', 'foouser']
        mygroup.save()

        # check ldap group was created
        new = LdapUserGroup.objects.get(name='re2o')
        self.assertEqual(new.name, 're2o')
        self.assertEqual(new.gid, 1010)
        self.assertEqual(new.members, ['someuser', 'foouser'])

    def test_create_re2ogroup(self):
        ListRight.objects.create(gid='1011', unix_name='admins', details='test')

        #check re2o
        lr = ListRight.objects.get(gid=1011)
        self.asserEqual(lr.gid, 1011)
        self.asserEqual(lr.details, 'test')



