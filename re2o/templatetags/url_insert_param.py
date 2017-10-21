# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Maël Kervella
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

"""
Templatetag used to write a URL (specified or current one) and adding
or inserting specific parameters into the query part without deleting
the other parameters.
"""

from django import template

register = template.Library()


@register.simple_tag
def url_insert_param(url="", **kwargs):
    """
    Return the URL with some specific parameters inserted into the query
    part. If a URL has already some parameters, those requested will be
    modified if already exisiting or will be added and the other parameters
    will stay unmodified.

    **Tag name**::

        url_insert_param

    **Parameters**:

        url (optional)
            The URL to use as a base. The parameters will be added to this URL.
            If not specified, it will only return the query part of the URL
            ("?a=foo&b=bar" for example).
            Example : "https://example.com/bar?foo=0&thing=abc"

        other arguments
            Any other key-value argument will be used. The key is considered as
            the name of the parameter to insert/modify and the value is the one
            used.
            Example : q="foo" search="bar" name="johnDoe"
                will return as ?<existing_param>&q=foo&search=bar&name=johnDoe

        **Usage**::

            {% url_insert_param [URL] [param1=val1 [param2=val2 [...]]] %}

        **Example**::

            {% url_insert_param a=0 b="bar" %}
                return "?a=0&b=bar"

            {% url_insert_param "url.net/foo.html" a=0 b="bar" %}
                return "url.net/foo.html?a=0&b=bar"

            {% url_insert_param "url.net/foo.html?c=keep" a=0 b="bar" %}
                return "url.net/foo.html?c=keep&a=0&b=bar"

            {% url_insert_param "url.net/foo.html?a=del" a=0 b="bar" %}
                return "url.net/foo.html?a=0&b=bar"

            {% url_insert_param "url.net/foo.html?a=del&c=keep" a=0 b="bar" %}
                return "url.net/foo.hmtl?a=0&c=keep&b=bar"
    """

    # Get existing parameters in the url
    params = {}
    if '?' in url:
        url, params = url.split('?', maxsplit=1)
        params = {
            p[:p.find('=')]: p[p.find('=')+1:] for p in params.split('&')
        }

    # Add the request parameters to the list of parameters
    for key, value in kwargs.items():
        params[key] = value

    # Write the url
    url += '?'
    for param, value in params.items():
        url += str(param) + '=' + str(value) + '&'

    # Remove the last '&' (or '?' if no parameters)
    return url[:-1]
