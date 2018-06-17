# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
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

import json
from rest_framework.test import APITestCase
from requests import codes

#import cotisations.models as cotisations
#import machines.models as machines
#import topologie.models as topologie
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
    no_auth_endpoints = [
        '/api/'
    ]
    auth_no_perm_endpoints = []
    auth_perm_endpoints = [
        '/api/cotisations/articles/',
#        '/api/cotisations/articles/<pk>/',
        '/api/cotisations/banques/',
#        '/api/cotisations/banques/<pk>/',
        '/api/cotisations/cotisations/',
#        '/api/cotisations/cotisations/<pk>/',
        '/api/cotisations/factures/',
#        '/api/cotisations/factures/<pk>/',
        '/api/cotisations/paiements/',
#        '/api/cotisations/paiements/<pk>/',
        '/api/cotisations/ventes/',
#        '/api/cotisations/ventes/<pk>/',
        '/api/machines/domains/',
#        '/api/machines/domains/<pk>/',
        '/api/machines/extensions/',
#        '/api/machines/extensions/<pk>/',
        '/api/machines/interfaces/',
#        '/api/machines/interfaces/<pk>/',
        '/api/machines/iplists/',
#        '/api/machines/iplists/<pk>/',
        '/api/machines/iptypes/',
#        '/api/machines/iptypes/<pk>/',
        '/api/machines/ipv6lists/',
#        '/api/machines/ipv6lists/<pk>/',
        '/api/machines/machines/',
#        '/api/machines/machines/<pk>/',
        '/api/machines/machinetypes/',
#        '/api/machines/machinetypes/<pk>/',
        '/api/machines/mx/',
#        '/api/machines/mx/<pk>/',
        '/api/machines/nas/',
#        '/api/machines/nas/<pk>/',
        '/api/machines/ns/',
#        '/api/machines/ns/<pk>/',
        '/api/machines/ouvertureportlists/',
#        '/api/machines/ouvertureportlists/<pk>/',
        '/api/machines/ouvertureports/',
#        '/api/machines/ouvertureports/<pk>/',
        '/api/machines/servicelinks/',
#        '/api/machines/servicelinks/<pk>/',
        '/api/machines/services/',
#        '/api/machines/services/<pk>/',
        '/api/machines/soa/',
#        '/api/machines/soa/<pk>/',
        '/api/machines/srv/',
#        '/api/machines/srv/<pk>/',
        '/api/machines/txt/',
#        '/api/machines/txt/<pk>/',
        '/api/machines/vlans/',
#        '/api/machines/vlans/<pk>/',
        '/api/preferences/optionaluser/',
        '/api/preferences/optionalmachine/',
        '/api/preferences/optionaltopologie/',
        '/api/preferences/generaloption/',
        '/api/preferences/service/',
#        '/api/preferences/service/<pk>/',
        '/api/preferences/assooption/',
        '/api/preferences/homeoption/',
        '/api/preferences/mailmessageoption/',
        '/api/topologie/acesspoint/',
#        '/api/topologie/acesspoint/<pk>/',
        '/api/topologie/building/',
#        '/api/topologie/building/<pk>/',
        '/api/topologie/constructorswitch/',
#        '/api/topologie/constructorswitch/<pk>/',
        '/api/topologie/modelswitch/',
#        '/api/topologie/modelswitch/<pk>/',
        '/api/topologie/room/',
#        '/api/topologie/room/<pk>/',
        '/api/topologie/stack/',
#        '/api/topologie/stack/<pk>/',
        '/api/topologie/switch/',
#        '/api/topologie/switch/<pk>/',
        '/api/topologie/switchbay/',
#        '/api/topologie/switchbay/<pk>/',
        '/api/topologie/switchport/',
#        '/api/topologie/switchport/<pk>/',
        '/api/users/adherents/',
#        '/api/users/adherents/<pk>/',
        '/api/users/bans/',
#        '/api/users/bans/<pk>/',
        '/api/users/clubs/',
#        '/api/users/clubs/<pk>/',
        '/api/users/listrights/',
#        '/api/users/listrights/<pk>/',
        '/api/users/schools/',
#        '/api/users/schools/<pk>/',
        '/api/users/serviceusers/',
#        '/api/users/serviceusers/<pk>/',
        '/api/users/shells/',
#        '/api/users/shells/<pk>/',
        '/api/users/users/',
#        '/api/users/users/<pk>/',
        '/api/users/whitelists/',
#        '/api/users/whitelists/<pk>/',
        '/api/dns/zones/',
        '/api/dhcp/hostmacip/',
        '/api/mailing/standard',
        '/api/mailing/club',
        '/api/services/regen/',
    ]
    
    stduser = None
    superuser = None

    @classmethod
    def setUpTestData(cls):
        # A user with no rights
        cls.stduser = users.User.objects.create_user(
            "apistduser",
            "apistduser",
            "apistduser@example.net",
            "apistduser"
        )
        # A user with all the rights
        cls.superuser = users.User.objects.create_superuser(
            "apisuperuser",
            "apisuperuser",
            "apisuperuser@example.net",
            "apisuperuser"
        )

        # TODO :
        # Create 1 object of every model so there is an exisiting object
        # when quering for pk=1

    @classmethod
    def tearDownClass(cls):
        cls.stduser.delete()
        cls.superuser.delete()
        super().tearDownClass()

    def check_responses_code(self, urls, expected_code, formats=None,
                             assert_more=None):
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
        urls = [endpoint.replace('<pk>', '1')
                for endpoint in self.no_auth_endpoints]
        self.check_responses_code(urls, codes.ok)

    def test_auth_endpoints_with_no_auth(self):
        """Tests that every endpoint that does require to be authenticated,
        returns a Unauthorized (401) response when not authenticated.

        Raises:
            AssertionError: An endpoint did not have a 401 status code.
        """
        urls = [endpoint.replace('<pk>', '1') for endpoint in \
                self.auth_no_perm_endpoints + self.auth_perm_endpoints]
        self.check_responses_code(urls, codes.unauthorized)

    def test_no_auth_endpoints_with_auth(self):
        """Tests that every endpoint that does not require to be
        authenticated, returns a Ok (200) response when authenticated.

        Raises:
            AssertionError: An endpoint did not have a 200 status code.
        """
        self.client.force_authenticate(user=self.stduser)
        urls = [endpoint.replace('<pk>', '1')
                for endpoint in self.no_auth_endpoints]
        self.check_responses_code(urls, codes.ok)

    def test_auth_no_perm_endpoints_with_auth_and_no_perm(self):
        """Tests that every endpoint that does require to be authenticated and
        no special permissions, returns a Ok (200) response when authenticated
        but without permissions.

        Raises:
            AssertionError: An endpoint did not have a 200 status code.
        """
        self.client.force_authenticate(user=self.stduser)
        urls = [endpoint.replace('<pk>', '1')
                for endpoint in self.auth_no_perm_endpoints]
        self.check_responses_code(urls, codes.ok)

    def test_auth_perm_endpoints_with_auth_and_no_perm(self):
        """Tests that every endpoint that does require to be authenticated and
        special permissions, returns a Forbidden (403) response when
        authenticated but without permissions.

        Raises:
            AssertionError: An endpoint did not have a 403 status code.
        """
        self.client.force_authenticate(user=self.stduser)
        urls = [endpoint.replace('<pk>', '1')
                for endpoint in self.auth_perm_endpoints]
        self.check_responses_code(urls, codes.forbidden)

    def test_auth_endpoints_with_auth_and_perm(self):
        """Tests that every endpoint that does require to be authenticated,
        returns a Ok (200) response when authenticated with all permissions.

        Raises:
            AssertionError: An endpoint did not have a 200 status code.
        """
        self.client.force_authenticate(user=self.superuser)
        urls = [endpoint.replace('<pk>', '1') for endpoint \
                in self.auth_no_perm_endpoints + self.auth_perm_endpoints]
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
        urls = [endpoint.replace('<pk>', '42') for endpoint in \
                self.no_auth_endpoints + self.auth_no_perm_endpoints + \
                self.auth_perm_endpoints if '<pk>' in endpoint]
        self.check_responses_code(urls, codes.not_found)

    def test_formats(self):
        """Tests that every endpoint returns a Ok (200) response when using
        different formats. Also checks that 'json' format returns a valid
        JSON object.

        Raises:
            AssertionError: An endpoint did not have a 200 status code.
        """
        self.client.force_authenticate(user=self.superuser)
        
        urls = [endpoint.replace('<pk>', '1') for endpoint in \
                self.no_auth_endpoints + self.auth_no_perm_endpoints + \
                self.auth_perm_endpoints]

        def assert_more(response, url, format):
            """Assert the response is valid json when format is json"""
            if format is 'json':
                json.loads(response.content.decode())

        self.check_responses_code(urls, codes.ok,
                                  formats=[None, 'json', 'api'],
                                  assert_more=assert_more)

class APIPaginationTestCase(APITestCase):
    """Test case to check that the pagination is used on all endpoints that
    should use it.

    Attributes:
        endpoints: A list of endpoints that should use the pagination.
        superuser: A superuser used in the tests to access the endpoints.
    """

    endpoints = [
        '/api/cotisations/articles/',
        '/api/cotisations/banques/',
        '/api/cotisations/cotisations/',
        '/api/cotisations/factures/',
        '/api/cotisations/paiements/',
        '/api/cotisations/ventes/',
        '/api/machines/domains/',
        '/api/machines/extensions/',
        '/api/machines/interfaces/',
        '/api/machines/iplists/',
        '/api/machines/iptypes/',
        '/api/machines/ipv6lists/',
        '/api/machines/machines/',
        '/api/machines/machinetypes/',
        '/api/machines/mx/',
        '/api/machines/nas/',
        '/api/machines/ns/',
        '/api/machines/ouvertureportlists/',
        '/api/machines/ouvertureports/',
        '/api/machines/servicelinks/',
        '/api/machines/services/',
        '/api/machines/soa/',
        '/api/machines/srv/',
        '/api/machines/txt/',
        '/api/machines/vlans/',
        '/api/preferences/service/',
        '/api/topologie/acesspoint/',
        '/api/topologie/building/',
        '/api/topologie/constructorswitch/',
        '/api/topologie/modelswitch/',
        '/api/topologie/room/',
        '/api/topologie/stack/',
        '/api/topologie/switch/',
        '/api/topologie/switchbay/',
        '/api/topologie/switchport/',
        '/api/users/adherents/',
        '/api/users/bans/',
        '/api/users/clubs/',
        '/api/users/listrights/',
        '/api/users/schools/',
        '/api/users/serviceusers/',
        '/api/users/shells/',
        '/api/users/users/',
        '/api/users/whitelists/',
        '/api/dns/zones/',
        '/api/dhcp/hostmacip/',
        '/api/mailing/standard',
        '/api/mailing/club',
        '/api/services/regen/',
    ]
    superuser = None

    @classmethod
    def setUpTestData(cls):
        # A user with all the rights
        cls.superuser = users.User.objects.create_superuser(
            "apisuperuser",
            "apisuperuser",
            "apisuperuser@example.net",
            "apisuperuser"
        )

    @classmethod
    def tearDownClass(cls):
        cls.superuser.delete()
        super().tearDownClass()

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
                response = self.client.get(url, format='json')
                res_json = json.loads(response.content.decode())
                assert 'count' in res_json.keys()
                assert 'next' in res_json.keys()
                assert 'previous' in res_json.keys()
                assert 'results' in res_json.keys()
                assert not len('results') > 100

