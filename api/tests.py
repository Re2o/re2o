# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018 Maël Kervella
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
"""Defines the test suite for the API
"""

import datetime
import json

from requests import codes
from rest_framework.test import APITestCase

import cotisations.models as cotisations
import machines.models as machines
import preferences.models as preferences
import topologie.models as topologie
import users.models as users


class APIEndpointsTestCase(APITestCase):
    """Test case to test that all endpoints are reachable with respects to
    authentication and permission checks.

    Attributes:
        no_auth_endpoints: A list of endpoints that should be reachable
            without authentication.
        auth_no_perm_endpoints: A list of endpoints that should be reachable
            when being authenticated but without permissions.
        auth_perm_endpoints: A list of endpoints that should be reachable
            when being authenticated and having the correct permissions.
        stduser: A standard user with no permission used for the tests and
            initialized at the beggining of this test case.
        superuser: A superuser (with all permissions) used for the tests and
            initialized at the beggining of this test case.
    """

    no_auth_endpoints = ["/api/"]
    auth_no_perm_endpoints = []
    auth_perm_endpoints = [
        "/api/cotisations/article/",
        "/api/cotisations/article/1/",
        "/api/cotisations/banque/",
        "/api/cotisations/banque/1/",
        "/api/cotisations/cotisation/",
        "/api/cotisations/cotisation/1/",
        "/api/cotisations/facture/",
        "/api/cotisations/facture/1/",
        "/api/cotisations/paiement/",
        "/api/cotisations/paiement/1/",
        "/api/cotisations/vente/",
        "/api/cotisations/vente/1/",
        "/api/machines/domain/",
        "/api/machines/domain/1/",
        "/api/machines/extension/",
        "/api/machines/extension/1/",
        "/api/machines/interface/",
        "/api/machines/interface/1/",
        "/api/machines/iplist/",
        "/api/machines/iplist/1/",
        "/api/machines/iptype/",
        "/api/machines/iptype/1/",
        "/api/machines/ipv6list/",
        "/api/machines/ipv6list/1/",
        "/api/machines/machine/",
        "/api/machines/machine/1/",
        "/api/machines/machinetype/",
        "/api/machines/machinetype/1/",
        "/api/machines/mx/",
        "/api/machines/mx/1/",
        "/api/machines/nas/",
        "/api/machines/nas/1/",
        "/api/machines/ns/",
        "/api/machines/ns/1/",
        "/api/machines/ouvertureportlist/",
        "/api/machines/ouvertureportlist/1/",
        "/api/machines/ouvertureport/",
        "/api/machines/ouvertureport/1/",
        "/api/machines/servicelink/",
        "/api/machines/servicelink/1/",
        "/api/machines/service/",
        "/api/machines/service/1/",
        "/api/machines/soa/",
        "/api/machines/soa/1/",
        "/api/machines/srv/",
        "/api/machines/srv/1/",
        "/api/machines/txt/",
        "/api/machines/txt/1/",
        "/api/machines/vlan/",
        "/api/machines/vlan/1/",
        "/api/preferences/optionaluser/",
        "/api/preferences/optionalmachine/",
        "/api/preferences/optionaltopologie/",
        "/api/preferences/generaloption/",
        "/api/preferences/service/",
        "/api/preferences/service/1/",
        "/api/preferences/assooption/",
        "/api/preferences/homeoption/",
        "/api/preferences/mailmessageoption/",
        "/api/topologie/acesspoint/",
        # 2nd machine to be create (machines_machine_1, topologie_accesspoint_1)
        "/api/topologie/acesspoint/2/",
        "/api/topologie/building/",
        "/api/topologie/building/1/",
        "/api/topologie/constructorswitch/",
        "/api/topologie/constructorswitch/1/",
        "/api/topologie/modelswitch/",
        "/api/topologie/modelswitch/1/",
        "/api/topologie/room/",
        "/api/topologie/room/1/",
        "/api/topologie/server/",
        # 3rd machine to be create (machines_machine_1, topologie_accesspoint_1,
        # topologie_server_1)
        "/api/topologie/server/3/",
        "/api/topologie/stack/",
        "/api/topologie/stack/1/",
        "/api/topologie/switch/",
        # 4th machine to be create (machines_machine_1, topologie_accesspoint_1,
        # topologie_server_1, topologie_switch_1)
        "/api/topologie/switch/4/",
        "/api/topologie/switchbay/",
        "/api/topologie/switchbay/1/",
        "/api/topologie/switchport/",
        "/api/topologie/switchport/1/",
        "/api/topologie/switchport/2/",
        "/api/topologie/switchport/3/",
        "/api/users/adherent/",
        # 3rd user to be create (stduser, superuser, users_adherent_1)
        "/api/users/adherent/3/",
        "/api/users/ban/",
        "/api/users/ban/1/",
        "/api/users/club/",
        # 4th user to be create (stduser, superuser, users_adherent_1,
        # users_club_1)
        "/api/users/club/4/",
        "/api/users/listright/",
        # TODO: Merge !145
        #        '/api/users/listright/1/',
        "/api/users/school/",
        "/api/users/school/1/",
        "/api/users/serviceuser/",
        "/api/users/serviceuser/1/",
        "/api/users/shell/",
        "/api/users/shell/1/",
        "/api/users/user/",
        "/api/users/user/1/",
        "/api/users/whitelist/",
        "/api/users/whitelist/1/",
        "/api/dns/zones/",
        "/api/dhcp/hostmacip/",
        "/api/mailing/standard",
        "/api/mailing/club",
        "/api/services/regen/",
    ]
    not_found_endpoints = [
        "/api/cotisations/article/4242/",
        "/api/cotisations/banque/4242/",
        "/api/cotisations/cotisation/4242/",
        "/api/cotisations/facture/4242/",
        "/api/cotisations/paiement/4242/",
        "/api/cotisations/vente/4242/",
        "/api/machines/domain/4242/",
        "/api/machines/extension/4242/",
        "/api/machines/interface/4242/",
        "/api/machines/iplist/4242/",
        "/api/machines/iptype/4242/",
        "/api/machines/ipv6list/4242/",
        "/api/machines/machine/4242/",
        "/api/machines/machinetype/4242/",
        "/api/machines/mx/4242/",
        "/api/machines/nas/4242/",
        "/api/machines/ns/4242/",
        "/api/machines/ouvertureportlist/4242/",
        "/api/machines/ouvertureport/4242/",
        "/api/machines/servicelink/4242/",
        "/api/machines/service/4242/",
        "/api/machines/soa/4242/",
        "/api/machines/srv/4242/",
        "/api/machines/txt/4242/",
        "/api/machines/vlan/4242/",
        "/api/preferences/service/4242/",
        "/api/topologie/acesspoint/4242/",
        "/api/topologie/building/4242/",
        "/api/topologie/constructorswitch/4242/",
        "/api/topologie/modelswitch/4242/",
        "/api/topologie/room/4242/",
        "/api/topologie/server/4242/",
        "/api/topologie/stack/4242/",
        "/api/topologie/switch/4242/",
        "/api/topologie/switchbay/4242/",
        "/api/topologie/switchport/4242/",
        "/api/users/adherent/4242/",
        "/api/users/ban/4242/",
        "/api/users/club/4242/",
        "/api/users/listright/4242/",
        "/api/users/school/4242/",
        "/api/users/serviceuser/4242/",
        "/api/users/shell/4242/",
        "/api/users/user/4242/",
        "/api/users/whitelist/4242/",
    ]

    stduser = None
    superuser = None

    @classmethod
    def setUpTestData(cls):
        # Be aware that every object created here is never actually committed
        # to the database. TestCase uses rollbacks after each test to cancel all
        # modifications and recreates the data defined here before each test.
        # For more details, see
        # https://docs.djangoproject.com/en/1.10/topics/testing/tools/#testcase

        super(APIEndpointsTestCase, cls).setUpClass()

        # A user with no rights
        cls.stduser = users.User.objects.create_user(
            "apistduser", "apistduser", "apistduser@example.net", "apistduser"
        )
        # A user with all the rights
        cls.superuser = users.User.objects.create_superuser(
            "apisuperuser", "apisuperuser", "apisuperuser@example.net", "apisuperuser"
        )

        # Creates 1 instance for each object so the "details" endpoints
        # can be tested too. Objects need to be created in the right order.
        # Dependencies (relatedFields, ...) are highlighted by a comment at
        # the end of the concerned line (# Dep <model>).
        cls.users_school_1 = users.School.objects.create(name="users_school_1")
        cls.users_school_1.save()
        cls.users_listshell_1 = users.ListShell.objects.create(
            shell="users_listshell_1"
        )
        cls.users_adherent_1 = users.Adherent.objects.create(
            password="password",
            last_login=datetime.datetime.now(datetime.timezone.utc),
            surname="users_adherent_1",
            pseudo="usersadherent1",
            email="users_adherent_1@example.net",
            school=cls.users_school_1,  # Dep users.School
            shell=cls.users_listshell_1,  # Dep users.ListShell
            comment="users Adherent 1 comment",
            pwd_ntlm="",
            state=users.User.STATES[0][0],
            registered=datetime.datetime.now(datetime.timezone.utc),
            telephone="0123456789",
            uid_number=21102,
            rezo_rez_uid=21102,
        )
        cls.users_user_1 = cls.users_adherent_1
        cls.cotisations_article_1 = cotisations.Article.objects.create(
            name="cotisations_article_1",
            prix=10,
            duration=1,
            type_user=cotisations.Article.USER_TYPES[0][0],
            type_cotisation=cotisations.Article.COTISATION_TYPE[0][0],
        )
        cls.cotisations_banque_1 = cotisations.Banque.objects.create(
            name="cotisations_banque_1"
        )
        cls.cotisations_paiement_1 = cotisations.Paiement.objects.create(
            moyen="cotisations_paiement_1",
            type_paiement=cotisations.Paiement.PAYMENT_TYPES[0][0],
        )
        cls.cotisations_facture_1 = cotisations.Facture.objects.create(
            user=cls.users_user_1,  # Dep users.User
            paiement=cls.cotisations_paiement_1,  # Dep cotisations.Paiement
            banque=cls.cotisations_banque_1,  # Dep cotisations.Banque
            cheque="1234567890",
            date=datetime.datetime.now(datetime.timezone.utc),
            valid=True,
            control=False,
        )
        cls.cotisations_vente_1 = cotisations.Vente.objects.create(
            facture=cls.cotisations_facture_1,  # Dep cotisations.Facture
            number=2,
            name="cotisations_vente_1",
            prix=10,
            duration=1,
            type_cotisation=cotisations.Vente.COTISATION_TYPE[0][0],
        )
        # A cotisation is automatically created by the Vente object and
        # trying to create another cotisation associated with this vente
        # will fail so we simply retrieve it so it can be used in the tests
        cls.cotisations_cotisation_1 = cotisations.Cotisation.objects.get(
            vente=cls.cotisations_vente_1  # Dep cotisations.Vente
        )
        cls.machines_machine_1 = machines.Machine.objects.create(
            user=cls.users_user_1,  # Dep users.User
            name="machines_machine_1",
            active=True,
        )
        cls.machines_ouvertureportlist_1 = machines.OuverturePortList.objects.create(
            name="machines_ouvertureportlist_1"
        )
        cls.machines_soa_1 = machines.SOA.objects.create(
            name="machines_soa_1",
            mail="postmaster@example.net",
            refresh=86400,
            retry=7200,
            expire=3600000,
            ttl=172800,
        )
        cls.machines_extension_1 = machines.Extension.objects.create(
            name="machines_extension_1",
            need_infra=False,
            # Do not set origin because of circular dependency
            origin_v6="2001:db8:1234::",
            soa=cls.machines_soa_1,  # Dep machines.SOA
        )
        cls.machines_vlan_1 = machines.Vlan.objects.create(
            vlan_id=0, name="machines_vlan_1", comment="machines Vlan 1"
        )
        cls.machines_iptype_1 = machines.IpType.objects.create(
            type="machines_iptype_1",
            extension=cls.machines_extension_1,  # Dep machines.Extension
            need_infra=False,
            domaine_ip_start="10.0.0.1",
            domaine_ip_stop="10.0.0.255",
            prefix_v6="2001:db8:1234::",
            vlan=cls.machines_vlan_1,  # Dep machines.Vlan
            ouverture_ports=cls.machines_ouvertureportlist_1,  # Dep machines.OuverturePortList
        )
        # All IPs in the IpType range are autocreated so we can't create
        # new ones and thus we only retrieve it if needed in the tests
        cls.machines_iplist_1 = machines.IpList.objects.get(
            ipv4="10.0.0.1", ip_type=cls.machines_iptype_1  # Dep machines.IpType
        )
        cls.machines_machinetype_1 = machines.MachineType.objects.create(
            type="machines_machinetype_1",
            ip_type=cls.machines_iptype_1,  # Dep machines.IpType
        )
        cls.machines_interface_1 = machines.Interface.objects.create(
            ipv4=cls.machines_iplist_1,  # Dep machines.IpList
            mac_address="00:00:00:00:00:00",
            machine=cls.machines_machine_1,  # Dep machines.Machine
            type=cls.machines_machinetype_1,  # Dep machines.MachineType
            details="machines Interface 1",
            # port_lists=[cls.machines_ouvertureportlist_1]  # Dep machines.OuverturePortList
        )
        cls.machines_domain_1 = machines.Domain.objects.create(
            interface_parent=cls.machines_interface_1,  # Dep machines.Interface
            name="machinesdomain",
            extension=cls.machines_extension_1  # Dep machines.Extension
            # Do no define cname for circular dependency
        )
        cls.machines_mx_1 = machines.Mx.objects.create(
            zone=cls.machines_extension_1,  # Dep machines.Extension
            priority=10,
            name=cls.machines_domain_1,  # Dep machines.Domain
        )
        cls.machines_ns_1 = machines.Ns.objects.create(
            zone=cls.machines_extension_1,  # Dep machines.Extension
            ns=cls.machines_domain_1,  # Dep machines.Domain
        )
        cls.machines_txt_1 = machines.Txt.objects.create(
            zone=cls.machines_extension_1,  # Dep machines.Extension
            field1="machines_txt_1",
            field2="machies Txt 1",
        )
        cls.machines_srv_1 = machines.Srv.objects.create(
            service="machines_srv_1",
            protocole=machines.Srv.TCP,
            extension=cls.machines_extension_1,  # Dep machines.Extension
            ttl=172800,
            priority=0,
            port=1,
            target=cls.machines_domain_1,  # Dep machines.Domain
        )
        cls.machines_ipv6list_1 = machines.Ipv6List.objects.create(
            ipv6="2001:db8:1234::",
            interface=cls.machines_interface_1,  # Dep machines.Interface
            slaac_ip=False,
        )
        cls.machines_service_1 = machines.Service.objects.create(
            service_type="machines_service_1",
            min_time_regen=datetime.timedelta(minutes=1),
            regular_time_regen=datetime.timedelta(hours=1)
            # Do not define service_link because circular dependency
        )
        cls.machines_servicelink_1 = machines.Service_link.objects.create(
            service=cls.machines_service_1,  # Dep machines.Service
            server=cls.machines_interface_1,  # Dep machines.Interface
            last_regen=datetime.datetime.now(datetime.timezone.utc),
            asked_regen=False,
        )
        cls.machines_ouvertureport_1 = machines.OuverturePort.objects.create(
            begin=1,
            end=2,
            port_list=cls.machines_ouvertureportlist_1,  # Dep machines.OuverturePortList
            protocole=machines.OuverturePort.TCP,
            io=machines.OuverturePort.OUT,
        )
        cls.machines_nas_1 = machines.Nas.objects.create(
            name="machines_nas_1",
            nas_type=cls.machines_machinetype_1,  # Dep machines.MachineType
            machine_type=cls.machines_machinetype_1,  # Dep machines.MachineType
            port_access_mode=machines.Nas.AUTH[0][0],
            autocapture_mac=False,
        )
        cls.preferences_service_1 = preferences.Service.objects.create(
            name="preferences_service_1",
            url="https://example.net",
            description="preferences Service 1",
            image="/media/logo/none.png",
        )
        cls.topologie_stack_1 = topologie.Stack.objects.create(
            name="topologie_stack_1",
            stack_id="1",
            details="topologie Stack 1",
            member_id_min=1,
            member_id_max=10,
        )
        cls.topologie_accespoint_1 = topologie.AccessPoint.objects.create(
            user=cls.users_user_1,  # Dep users.User
            name="machines_machine_1",
            active=True,
            location="topologie AccessPoint 1",
        )
        cls.topologie_server_1 = topologie.Server.objects.create(
            user=cls.users_user_1,  # Dep users.User
            name="machines_machine_1",
            active=True,
        )
        cls.topologie_building_1 = topologie.Building.objects.create(
            name="topologie_building_1"
        )
        cls.topologie_switchbay_1 = topologie.SwitchBay.objects.create(
            name="topologie_switchbay_1",
            building=cls.topologie_building_1,  # Dep topologie.Building
            info="topologie SwitchBay 1",
        )
        cls.topologie_constructorswitch_1 = topologie.ConstructorSwitch.objects.create(
            name="topologie_constructorswitch_1"
        )
        cls.topologie_modelswitch_1 = topologie.ModelSwitch.objects.create(
            reference="topologie_modelswitch_1",
            constructor=cls.topologie_constructorswitch_1,  # Dep topologie.ConstructorSwitch
        )
        cls.topologie_switch_1 = topologie.Switch.objects.create(
            user=cls.users_user_1,  # Dep users.User
            name="machines_machine_1",
            active=True,
            number=10,
            stack=cls.topologie_stack_1,  # Dep topologie.Stack
            stack_member_id=1,
            model=cls.topologie_modelswitch_1,  # Dep topologie.ModelSwitch
            switchbay=cls.topologie_switchbay_1,  # Dep topologie.SwitchBay
        )
        cls.topologie_room_1 = topologie.Room.objects.create(
            name="topologie_romm_1", details="topologie Room 1"
        )
        cls.topologie_port_1 = topologie.Port.objects.create(
            switch=cls.topologie_switch_1,  # Dep topologie.Switch
            port=1,
            room=cls.topologie_room_1,  # Dep topologie.Room
            radius=topologie.Port.STATES[0][0],
            vlan_force=cls.machines_vlan_1,  # Dep machines.Vlan
            details="topologie_switch_1",
        )
        cls.topologie_port_2 = topologie.Port.objects.create(
            switch=cls.topologie_switch_1,  # Dep topologie.Switch
            port=2,
            machine_interface=cls.machines_interface_1,  # Dep machines.Interface
            radius=topologie.Port.STATES[0][0],
            vlan_force=cls.machines_vlan_1,  # Dep machines.Vlan
            details="topologie_switch_1",
        )
        cls.topologie_port_3 = topologie.Port.objects.create(
            switch=cls.topologie_switch_1,  # Dep topologie.Switch
            port=3,
            room=cls.topologie_room_1,  # Dep topologie.Room
            radius=topologie.Port.STATES[0][0],
            # Do not defines related because circular dependency  # Dep machines.Vlan
            details="topologie_switch_1",
        )
        cls.users_ban_1 = users.Ban.objects.create(
            user=cls.users_user_1,  # Dep users.User
            raison="users Ban 1",
            date_start=datetime.datetime.now(datetime.timezone.utc),
            date_end=datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=1),
            state=users.Ban.STATES[0][0],
        )
        cls.users_club_1 = users.Club.objects.create(
            password="password",
            last_login=datetime.datetime.now(datetime.timezone.utc),
            surname="users_club_1",
            pseudo="usersclub1",
            email="users_club_1@example.net",
            school=cls.users_school_1,  # Dep users.School
            shell=cls.users_listshell_1,  # Dep users.ListShell
            comment="users Club 1 comment",
            pwd_ntlm="",
            state=users.User.STATES[0][0],
            registered=datetime.datetime.now(datetime.timezone.utc),
            telephone="0123456789",
            uid_number=21103,
            rezo_rez_uid=21103,
        )
        # Need merge of MR145 to work
        # TODO: Merge !145
        #        cls.users_listright_1 = users.ListRight.objects.create(
        #            unix_name="userslistright",
        #            gid=601,
        #            critical=False,
        #            details="userslistright"
        #        )
        cls.users_serviceuser_1 = users.ServiceUser.objects.create(
            password="password",
            last_login=datetime.datetime.now(datetime.timezone.utc),
            pseudo="usersserviceuser1",
            access_group=users.ServiceUser.ACCESS[0][0],
            comment="users ServiceUser 1",
        )
        cls.users_whitelist_1 = users.Whitelist.objects.create(
            user=cls.users_user_1,
            raison="users Whitelist 1",
            date_start=datetime.datetime.now(datetime.timezone.utc),
            date_end=datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=1),
        )

    def check_responses_code(self, urls, expected_code, formats=None, assert_more=None):
        """Utility function to test if a list of urls answer an expected code.

        Args:
            urls: The list of urls to test
            expected_code: The HTTP return code expected
            formats: The list of formats to use for the request. Default is to
                only test `None` format.
            assert_more: An optional function to assert more specific data in
                the same test. The response object, the url and the format
                used are passed as arguments.

        Raises:
            AssertionError: The response got did not have the expected status
                code.
            Any exception raised in the evalutation of `assert_more`.
        """
        if formats is None:
            formats = [None]
        for url in urls:
            for format in formats:
                with self.subTest(url=url, format=format):
                    response = self.client.get(url, format=format)
                    assert response.status_code == expected_code
                    if assert_more is not None:
                        assert_more(response, url, format)

    def test_no_auth_endpoints_with_no_auth(self):
        """Tests that every endpoint that does not require to be
        authenticated, returns a Ok (200) response when not authenticated.

        Raises:
            AssertionError: An endpoint did not have a 200 status code.
        """
        urls = self.no_auth_endpoints
        self.check_responses_code(urls, codes.ok)

    def test_auth_endpoints_with_no_auth(self):
        """Tests that every endpoint that does require to be authenticated,
        returns a Unauthorized (401) response when not authenticated.

        Raises:
            AssertionError: An endpoint did not have a 401 status code.
        """
        urls = self.auth_no_perm_endpoints + self.auth_perm_endpoints
        self.check_responses_code(urls, codes.unauthorized)

    def test_no_auth_endpoints_with_auth(self):
        """Tests that every endpoint that does not require to be
        authenticated, returns a Ok (200) response when authenticated.

        Raises:
            AssertionError: An endpoint did not have a 200 status code.
        """
        self.client.force_authenticate(user=self.stduser)
        urls = self.no_auth_endpoints
        self.check_responses_code(urls, codes.ok)

    def test_auth_no_perm_endpoints_with_auth_and_no_perm(self):
        """Tests that every endpoint that does require to be authenticated and
        no special permissions, returns a Ok (200) response when authenticated
        but without permissions.

        Raises:
            AssertionError: An endpoint did not have a 200 status code.
        """
        self.client.force_authenticate(user=self.stduser)
        urls = self.auth_no_perm_endpoints
        self.check_responses_code(urls, codes.ok)

    def test_auth_perm_endpoints_with_auth_and_no_perm(self):
        """Tests that every endpoint that does require to be authenticated and
        special permissions, returns a Forbidden (403) response when
        authenticated but without permissions.

        Raises:
            AssertionError: An endpoint did not have a 403 status code.
        """
        self.client.force_authenticate(user=self.stduser)
        urls = self.auth_perm_endpoints
        self.check_responses_code(urls, codes.forbidden)

    def test_auth_endpoints_with_auth_and_perm(self):
        """Tests that every endpoint that does require to be authenticated,
        returns a Ok (200) response when authenticated with all permissions.

        Raises:
            AssertionError: An endpoint did not have a 200 status code.
        """
        self.client.force_authenticate(user=self.superuser)
        urls = self.auth_no_perm_endpoints + self.auth_perm_endpoints
        self.check_responses_code(urls, codes.ok)

    def test_endpoints_not_found(self):
        """Tests that every endpoint that uses a primary key parameter,
        returns a Not Found (404) response when queried with non-existing
        primary key.

        Raises:
            AssertionError: An endpoint did not have a 404 status code.
        """
        self.client.force_authenticate(user=self.superuser)
        # Select only the URLs with '<pk>' and replace it with '42'
        urls = self.not_found_endpoints
        self.check_responses_code(urls, codes.not_found)

    def test_formats(self):
        """Tests that every endpoint returns a Ok (200) response when using
        different formats. Also checks that 'json' format returns a valid
        JSON object.

        Raises:
            AssertionError: An endpoint did not have a 200 status code.
        """
        self.client.force_authenticate(user=self.superuser)

        urls = (
            self.no_auth_endpoints
            + self.auth_no_perm_endpoints
            + self.auth_perm_endpoints
        )

        def assert_more(response, url, format):
            """Assert the response is valid json when format is json"""
            if format is "json":
                json.loads(response.content.decode())

        self.check_responses_code(
            urls, codes.ok, formats=[None, "json", "api"], assert_more=assert_more
        )


class APIPaginationTestCase(APITestCase):
    """Test case to check that the pagination is used on all endpoints that
    should use it.

    Attributes:
        endpoints: A list of endpoints that should use the pagination.
        superuser: A superuser used in the tests to access the endpoints.
    """

    endpoints = [
        "/api/cotisations/article/",
        "/api/cotisations/banque/",
        "/api/cotisations/cotisation/",
        "/api/cotisations/facture/",
        "/api/cotisations/paiement/",
        "/api/cotisations/vente/",
        "/api/machines/domain/",
        "/api/machines/extension/",
        "/api/machines/interface/",
        "/api/machines/iplist/",
        "/api/machines/iptype/",
        "/api/machines/ipv6list/",
        "/api/machines/machine/",
        "/api/machines/machinetype/",
        "/api/machines/mx/",
        "/api/machines/nas/",
        "/api/machines/ns/",
        "/api/machines/ouvertureportlist/",
        "/api/machines/ouvertureport/",
        "/api/machines/servicelink/",
        "/api/machines/service/",
        "/api/machines/soa/",
        "/api/machines/srv/",
        "/api/machines/txt/",
        "/api/machines/vlan/",
        "/api/preferences/service/",
        "/api/topologie/acesspoint/",
        "/api/topologie/building/",
        "/api/topologie/constructorswitch/",
        "/api/topologie/modelswitch/",
        "/api/topologie/room/",
        "/api/topologie/server/",
        "/api/topologie/stack/",
        "/api/topologie/switch/",
        "/api/topologie/switchbay/",
        "/api/topologie/switchport/",
        "/api/users/adherent/",
        "/api/users/ban/",
        "/api/users/club/",
        "/api/users/listright/",
        "/api/users/school/",
        "/api/users/serviceuser/",
        "/api/users/shell/",
        "/api/users/user/",
        "/api/users/whitelist/",
        "/api/dns/zones/",
        "/api/dhcp/hostmacip/",
        "/api/mailing/standard",
        "/api/mailing/club",
        "/api/services/regen/",
    ]
    superuser = None

    @classmethod
    def setUpTestData(cls):
        # A user with all the rights
        # We need to use a different username than for the first
        # test case because TestCase is using rollbacks which don't
        # trigger the ldap_sync() thus the LDAP still have data about
        # the old users.
        cls.superuser = users.User.objects.create_superuser(
            "apisuperuser2",
            "apisuperuser2",
            "apisuperuser2@example.net",
            "apisuperuser2",
        )

    @classmethod
    def tearDownClass(cls):
        cls.superuser.delete()
        super(APIPaginationTestCase, self).tearDownClass()

    def test_pagination(self):
        """Tests that every endpoint is using the pagination correctly.

        Raises:
            AssertionError: An endpoint did not have one the following keyword
                in the JSOn response: 'count', 'next', 'previous', 'results'
                or more that 100 results were returned.
        """
        self.client.force_authenticate(self.superuser)
        for url in self.endpoints:
            with self.subTest(url=url):
                response = self.client.get(url, format="json")
                res_json = json.loads(response.content.decode())
                assert "count" in res_json.keys()
                assert "next" in res_json.keys()
                assert "previous" in res_json.keys()
                assert "results" in res_json.keys()
                assert not len("results") > 100
