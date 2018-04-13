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

"""api.utils.

Set of various and usefull functions for the API app
"""

from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse


class JSONResponse(HttpResponse):
    """A JSON response that can be send as an HTTP response.
    Usefull in case of REST API.
    """

    def __init__(self, data, **kwargs):
        """Initialisz a JSONResponse object.

        Args:
            data: the data to render as JSON (often made of lists, dicts,
            strings, boolean and numbers). See `JSONRenderer.render(data)` for
            further details.

        Creates:
            An HTTPResponse containing the data in JSON format.
        """

        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class JSONError(JSONResponse):
    """A JSON response when the request failed.
    """

    def __init__(self, error_msg, data=None, **kwargs):
        """Initialise a JSONError object.

        Args:
            error_msg: A message explaining where the error is.
            data: An optional field for further data to send along.

        Creates:
            A JSONResponse containing a field `status` set to `error` and a
            field `reason` containing `error_msg`. If `data` argument has been
            given, a field `data` containing it is added to the JSON response.
        """

        response = {
            'status': 'error',
            'reason': error_msg
        }
        if data is not None:
            response['data'] = data
        super(JSONError, self).__init__(response, **kwargs)


class JSONSuccess(JSONResponse):
    """A JSON response when the request suceeded.
    """

    def __init__(self, data=None, **kwargs):
        """Initialise a JSONSucess object.

        Args:
            error_msg: A message explaining where the error is.
            data: An optional field for further data to send along.

        Creates:
            A JSONResponse containing a field `status` set to `sucess`. If
            `data` argument has been given, a field `data` containing it is
            added to the JSON response.
        """

        response = {
            'status': 'success',
        }
        if data is not None:
            response['data'] = data
        super(JSONSuccess, self).__init__(response, **kwargs)


def accept_method(methods):
    """Decorator to set a list of accepted request method.
    Check if the method used is accepted. If not, send a NotAllowed response.
    """

    def decorator(view):
        def wrapper(request, *args, **kwargs):
            if request.method in methods:
                return view(request, *args, **kwargs)
            else:
                return JSONError(
                    'Invalid request method. Request methods authorize are ' +
                    str(methods)
                )
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
