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

"""Defines the pagination classes used in the API to paginate the results.
"""

from rest_framework import pagination


class PageSizedPagination(pagination.PageNumberPagination):
    """Provide the possibility to control the page size by using the
    'page_size' parameter. The value 'all' can be used for this parameter
    to retrieve all the results in a single page.

    Attributes:
        page_size_query_param: The string to look for in the parameters of
            a query to get the page_size requested.
        all_pages_strings: A set of strings that can be used in the query to
            request all results in a single page.
        max_page_size: The maximum number of results a page can output no
            matter what is requested.
    """

    page_size_query_param = "page_size"
    all_pages_strings = ("all",)
    max_page_size = 10000

    def get_page_size(self, request):
        """Retrieve the size of the page according to the parameters of the
        request.

        Args:
            request: the request of the user

        Returns:
            A integer between 0 and `max_page_size` that represent the size
            of the page to use.
        """
        try:
            page_size_str = request.query_params[self.page_size_query_param]
            if page_size_str in self.all_pages_strings:
                return self.max_page_size
        except KeyError:
            pass

        return super(PageSizedPagination, self).get_page_size(request)
