# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Jean-Romain Garnier
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

from django import template
from .url_insert_param import url_insert_param

register = template.Library()

@register.simple_tag
def pagination_insert_page_and_id(url, page=1, id=None, **kwargs):
    """
    Return the URL with some specific parameters inserted into the query
    part. If a URL has already some parameters, those requested will be
    modified if already exisiting or will be added and the other parameters
    will stay unmodified. If parameters with the same name are already in the
    URL and a value is specified for this parameter, it will replace all
    existing parameters.

    **Tag name**::

        pagination_insert_page_and_id

    **Parameters**:

        url
            The URL to use as a base. The parameters will be added to this URL.

        page (optional)
            The page number (greater or equal to 1) to add as a parameter.
            If not specified, it will default to 1.

        id (optional)
            The ID to jump to in the page.
            If not specified, it will not be added.

        **Other accepted parameters***

        page_args (optional)
            The name of the parameter used to specify the page number.
            It must be specifically set as a keyword.
            If not specified, defaults to 1.
            Example: {% pagination_insert_page_and_id https://example.com 2 page_args="page_id" %}
                     returns https://example.com?page_id=2

        **Usage**::

            {% pagination_insert_page_and_id [URL] [page number] [go to id] %}

        **Example**::

            {% pagination_insert_page_and_id https://example.com/bar 2 settings %}
                return "https://example.com/bar?page=2#settings"

            {% pagination_insert_page_and_id https://example.com/bar?foo=0 2 %}
                return "https://example.com/bar?foo=0&page=2"

            {% pagination_insert_page_and_id https://example.com/bar?foo=0 2 page_arg="page_id" %}
                return "https://example.com/bar?foo=0&page_id=2"
    """

    page_arg = "page"
    if "page_arg" in kwargs and kwargs["page_arg"] is not None and len(kwargs["page_arg"]) > 0:
        page_arg = kwargs["page_arg"]

    args = { "url": url, page_arg: page}
    new_url = url_insert_param(**args)

    if id != None:
        new_url += "#" + str(id)

    return new_url
