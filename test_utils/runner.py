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

"""Defines the custom runners for Re2o.
"""

import os.path

import volatildap
from django.conf import settings
from django.test.runner import DiscoverRunner

from users.models import (LdapServiceUser, LdapServiceUserGroup, LdapUser,
                          LdapUserGroup)

# The path of this file
__here = os.path.dirname(os.path.realpath(__file__))
# The absolute path where to find the schemas for the LDAP
schema_path = os.path.abspath(os.path.join(__here, "ldap", "schema"))
# The absolute path of the "radius.schema" file
radius_schema_path = os.path.join(schema_path, "radius.schema")
# The absolute path of the "samba.schema" file
samba_schema_path = os.path.join(schema_path, "samba.schema")

# The suffix for the LDAP
suffix = "dc=example,dc=net"
# The admin CN of the LDAP
rootdn = "cn=admin," + suffix

# Defines all ldap_entry mandatory for Re2o under a key-value list format
# that can be used directly by volatildap. For more on how to generate this
# data, see https://gitlab.federez.net/re2o/scripts/blob/master/print_ldap_entries.py
ldapentry_Utilisateurs = (
    "cn=Utilisateurs," + suffix,
    {
        "cn": ["Utilisateurs"],
        "sambaSID": ["500"],
        "uid": ["Users"],
        "objectClass": ["posixGroup", "top", "sambaSamAccount", "radiusprofile"],
        "gidNumber": ["500"],
    },
)
ldapentry_groups = (
    "ou=groups," + suffix,
    {
        "ou": ["groups"],
        "objectClass": ["organizationalUnit"],
        "description": ["Groupes d'utilisateurs"],
    },
)
ldapentry_services = (
    "ou=services,ou=groups," + suffix,
    {
        "ou": ["services"],
        "objectClass": ["organizationalUnit"],
        "description": ["Groupes de comptes techniques"],
    },
)
ldapentry_service_users = (
    "ou=service-users," + suffix,
    {
        "ou": ["service-users"],
        "objectClass": ["organizationalUnit"],
        "description": ["Utilisateurs techniques de l'annuaire"],
    },
)
ldapentry_freeradius = (
    "cn=freeradius,ou=service-users," + suffix,
    {
        "cn": ["freeradius"],
        "objectClass": ["applicationProcess", "simpleSecurityObject"],
        "userPassword": ["FILL_IT"],
    },
)
ldapentry_nssauth = (
    "cn=nssauth,ou=service-users," + suffix,
    {
        "cn": ["nssauth"],
        "objectClass": ["applicationProcess", "simpleSecurityObject"],
        "userPassword": ["FILL_IT"],
    },
)
ldapentry_auth = (
    "cn=auth,ou=services,ou=groups," + suffix,
    {
        "cn": ["auth"],
        "objectClass": ["groupOfNames"],
        "member": ["cn=nssauth,ou=service-users," + suffix],
    },
)
ldapentry_posix = (
    "ou=posix,ou=groups," + suffix,
    {
        "ou": ["posix"],
        "objectClass": ["organizationalUnit"],
        "description": ["Groupes de comptes POSIX"],
    },
)
ldapentry_wifi = (
    "cn=wifi,ou=service-users," + suffix,
    {
        "cn": ["wifi"],
        "objectClass": ["applicationProcess", "simpleSecurityObject"],
        "userPassword": ["FILL_IT"],
    },
)
ldapentry_usermgmt = (
    "cn=usermgmt,ou=services,ou=groups," + suffix,
    {
        "cn": ["usermgmt"],
        "objectClass": ["groupOfNames"],
        "member": ["cn=wifi,ou=service-users," + suffix],
    },
)
ldapentry_replica = (
    "cn=replica,ou=service-users," + suffix,
    {
        "cn": ["replica"],
        "objectClass": ["applicationProcess", "simpleSecurityObject"],
        "userPassword": ["FILL_IT"],
    },
)
ldapentry_readonly = (
    "cn=readonly,ou=services,ou=groups," + suffix,
    {
        "cn": ["readonly"],
        "objectClass": ["groupOfNames"],
        "member": [
            "cn=replica,ou=service-users," + suffix,
            "cn=freeradius,ou=service-users," + suffix,
        ],
    },
)
ldapbasic = dict(
    [
        ldapentry_Utilisateurs,
        ldapentry_groups,
        ldapentry_services,
        ldapentry_service_users,
        ldapentry_freeradius,
        ldapentry_nssauth,
        ldapentry_auth,
        ldapentry_posix,
        ldapentry_wifi,
        ldapentry_usermgmt,
        ldapentry_replica,
        ldapentry_readonly,
    ]
)


class DiscoverLdapRunner(DiscoverRunner):
    """Discovers all the tests in the project

    This is a simple subclass of the default test runner
    `django.test.runner.DiscoverRunner` that creates a test LDAP
    right after the test databases are setup and destroys it right
    before the test databases are setup.
    It also ensure re2o's settings are using this new LDAP.
    """

    # The `volatildap.LdapServer` instance initiated with the minimal
    # structure required by Re2o
    ldap_server = volatildap.LdapServer(
        suffix=suffix,
        rootdn=rootdn,
        initial_data=ldapbasic,
        schemas=[
            "core.schema",
            "cosine.schema",
            "inetorgperson.schema",
            "nis.schema",
            radius_schema_path,
            samba_schema_path,
        ],
    )

    def __init__(self, *args, **kwargs):
        settings.DATABASES["ldap"]["USER"] = self.ldap_server.rootdn
        settings.DATABASES["ldap"]["PASSWORD"] = self.ldap_server.rootpw
        settings.DATABASES["ldap"]["NAME"] = self.ldap_server.uri
        settings.LDAP["base_user_dn"] = ldapentry_Utilisateurs[0]
        settings.LDAP["base_userservice_dn"] = ldapentry_service_users[0]
        settings.LDAP["base_usergroup_dn"] = ldapentry_posix[0]
        settings.LDAP["base_userservicegroup_dn"] = ldapentry_services[0]
        settings.LDAP["user_gid"] = ldapentry_Utilisateurs[1].get("gidNumber", ["500"])[
            0
        ]
        LdapUser.base_dn = settings.LDAP["base_user_dn"]
        LdapUserGroup.base_dn = settings.LDAP["base_usergroup_dn"]
        LdapServiceUser.base_dn = settings.LDAP["base_userservice_dn"]
        LdapServiceUserGroup.base_dn = settings.LDAP["base_userservicegroup_dn"]
        super(DiscoverLdapRunner, self).__init__(*args, **kwargs)

    def setup_databases(self, *args, **kwargs):
        ret = super(DiscoverLdapRunner, self).setup_databases(*args, **kwargs)
        print("Creating test LDAP with volatildap...")
        self.ldap_server.start()
        return ret

    def teardown_databases(self, *args, **kwargs):
        self.ldap_server.stop()
        print("Destroying test LDAP...")
        super(DiscoverLdapRunner, self).teardown_databases(*args, **kwargs)
