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

"""Defines the permission classes used in the API.
"""

from rest_framework import permissions, exceptions
from django.http import Http404
from . import acl


def can_see_api(*_, **__):
    """Check if a user can view the API.

    Returns:
        A function that takes a user as an argument and returns
        an ACL tuple that assert this user can see the API.
    """
    return lambda user: acl.can_view(user)


def _get_param_in_view(view, param_name):
    """Utility function to retrieve an attribute in a view passed in argument.

    Uses the result of `{view}.get_{param_name}()` if existing else uses the
    value of `{view}.{param_name}` directly.

    Args:
        view: The view where to look into.
        param_name: The name of the attribute to look for.

    Returns:
        The result of the getter function if found else the value of the
        attribute itself.

    Raises:
        AssertionError: None of the getter function or the attribute are
            defined in the view.
    """
    assert (
        hasattr(view, "get_" + param_name)
        or getattr(view, param_name, None) is not None
    ), (
        "cannot apply {} on a view that does not set "
        "`.{}` or have a `.get_{}()` method."
    ).format(
        self.__class__.__name__, param_name, param_name
    )

    if hasattr(view, "get_" + param_name):
        param = getattr(view, "get_" + param_name)()
        assert param is not None, ("{}.get_{}() returned None").format(
            view.__class__.__name__, param_name
        )
        return param
    return getattr(view, param_name)


class ACLPermission(permissions.BasePermission):
    """A permission class used to check the ACL to validate the permissions
    of a user.

    The view must define a `.get_perms_map()` or a `.perms_map` attribute.
    See the wiki for the syntax of this attribute.
    """

    @staticmethod
    def get_required_permissions(method, view):
        """Build the list of permissions required for the request to be
        accepted.

        Args:
            method: The HTTP method name used for the request.
            view: The view which is responding to the request.

        Returns:
            The list of ACL functions to apply to a user in order to check
            if he has the right permissions.

        Raises:
            AssertionError: None of `.get_perms_map()` or `.perms_map` are
                defined in the view.
            rest_framework.exception.MethodNotAllowed: The requested method
                is not allowed for this view.
        """
        perms_map = _get_param_in_view(view, "perms_map")

        if method not in perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [can_see_api()] + list(perms_map[method])

    def has_permission(self, request, view):
        """Check that the user has the permissions to perform the request.

        Args:
            request: The request performed.
            view: The view which is responding to the request.

        Returns:
            A boolean indicating if the user has the permission to
            perform the request.

        Raises:
            AssertionError: None of `.get_perms_map()` or `.perms_map` are
                defined in the view.
            rest_framework.exception.MethodNotAllowed: The requested method
                is not allowed for this view.
        """
        # Workaround to ensure ACLPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, "_ignore_model_permissions", False):
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        perms = self.get_required_permissions(request.method, view)

        return all(perm(request.user)[0] for perm in perms)


class AutodetectACLPermission(permissions.BasePermission):
    """A permission class used to autodetect the ACL needed to validate the
    permissions of a user based on the queryset of the view.

    The view must define a `.get_queryset()` or a `.queryset` attribute.

    Attributes:
        perms_map: The mapping of each valid HTTP method to the required
            model-based ACL permissions.
        perms_obj_map: The mapping of each valid HTTP method to the required
            object-based ACL permissions.
    """

    perms_map = {
        "GET": [can_see_api, lambda model: model.can_view_all],
        "OPTIONS": [can_see_api, lambda model: model.can_view_all],
        "HEAD": [can_see_api, lambda model: model.can_view_all],
        "POST": [can_see_api, lambda model: model.can_create],
        "PUT": [],  # No restrictions, apply to objects
        "PATCH": [],  # No restrictions, apply to objects
        "DELETE": [],  # No restrictions, apply to objects
    }
    perms_obj_map = {
        "GET": [can_see_api, lambda obj: obj.can_view],
        "OPTIONS": [can_see_api, lambda obj: obj.can_view],
        "HEAD": [can_see_api, lambda obj: obj.can_view],
        "POST": [],  # No restrictions, apply to models
        "PUT": [can_see_api, lambda obj: obj.can_edit],
        "PATCH": [can_see_api, lambda obj: obj.can_edit],
        "DELETE": [can_see_api, lambda obj: obj.can_delete],
    }

    def get_required_permissions(self, method, model):
        """Build the list of model-based permissions required for the
        request to be accepted.

        Args:
            method: The HTTP method name used for the request.
            view: The view which is responding to the request.

        Returns:
            The list of ACL functions to apply to a user in order to check
            if he has the right permissions.

        Raises:
            rest_framework.exception.MethodNotAllowed: The requested method
                is not allowed for this view.
        """
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm(model) for perm in self.perms_map[method]]

    def get_required_object_permissions(self, method, obj):
        """Build the list of object-based permissions required for the
        request to be accepted.

        Args:
            method: The HTTP method name used for the request.
            view: The view which is responding to the request.

        Returns:
            The list of ACL functions to apply to a user in order to check
            if he has the right permissions.

        Raises:
            rest_framework.exception.MethodNotAllowed: The requested method
                is not allowed for this view.
        """
        if method not in self.perms_obj_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm(obj) for perm in self.perms_obj_map[method]]

    @staticmethod
    def _queryset(view):
        return _get_param_in_view(view, "queryset")

    def has_permission(self, request, view):
        """Check that the user has the model-based permissions to perform
        the request.

        Args:
            request: The request performed.
            view: The view which is responding to the request.

        Returns:
            A boolean indicating if the user has the permission to
            perform the request.

        Raises:
            AssertionError: None of `.get_queryset()` or `.queryset` are
                defined in the view.
            rest_framework.exception.MethodNotAllowed: The requested method
                is not allowed for this view.
        """
        # Workaround to ensure ACLPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, "_ignore_model_permissions", False):
            return True

        # Bypass permission verifications if it is a functional view
        # (permissions are handled by ACL)
        if not getattr(view, "queryset", getattr(view, "get_queryset", None)):
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)

        return all(perm(request.user)[0] for perm in perms)

    def has_object_permission(self, request, view, obj):
        """Check that the user has the object-based permissions to perform
        the request.

        Args:
            request: The request performed.
            view: The view which is responding to the request.

        Returns:
            A boolean indicating if the user has the permission to
            perform the request.

        Raises:
            rest_framework.exception.MethodNotAllowed: The requested method
                is not allowed for this view.
        """
        # authentication checks have already executed via has_permission
        user = request.user

        perms = self.get_required_object_permissions(request.method, obj)

        if not all(perm(request.user)[0] for perm in perms):
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            SAFE_METHODS = ("GET", "OPTIONS", "HEAD",
                            "POST", "PUT", "PATCH", "DELETE")

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.get_required_object_permissions("GET", obj)
            if not read_perms(request.user)[0]:
                raise Http404

            # Has read permissions.
            return False

        return True
