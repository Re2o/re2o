from rest_framework import permissions, exceptions
from re2o.acl import can_create, can_edit, can_delete, can_view_all

from . import acl

def can_see_api(_):
    return lambda user: acl.can_view(user)


class DefaultACLPermission(permissions.BasePermission):
    """
    Permission subclass in charge of checking the ACL to determine
    if a user can access the models
    """
    perms_map = {
        'GET': [can_see_api, lambda model: model.can_view_all],
        'OPTIONS': [can_see_api, lambda model: model.can_view_all],
        'HEAD': [can_see_api, lambda model: model.can_view_all],
        'POST': [can_see_api, lambda model: model.can_create],
        'PUT': [],     # No restrictions, apply to objects
        'PATCH': [],   # No restrictions, apply to objects
        'DELETE': [],  # No restrictions, apply to objects
    }
    perms_obj_map = {
        'GET': [can_see_api, lambda obj: obj.can_view],
        'OPTIONS': [can_see_api, lambda obj: obj.can_view],
        'HEAD': [can_see_api, lambda obj: obj.can_view],
        'POST': [],    # No restrictions, apply to models
        'PUT': [can_see_api, lambda obj: obj.can_edit],
        'PATCH': [can_see_api, lambda obj: obj.can_edit],
        'DELETE': [can_see_api, lambda obj: obj.can_delete],
    }

    def get_required_permissions(self, method, model):
        """
        Given a model and an HTTP method, return the list of acl
        functions that the user is required to verify.
        """
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm(model) for perm in self.perms_map[method]]

    def get_required_object_permissions(self, method, obj):
        """
        Given an object and an HTTP method, return the list of acl
        functions that the user is required to verify.
        """
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm(obj) for perm in self.perms_map[method]]

    def _queryset(self, view):
        """
        Return the queryset associated with view and raise an error
        is there is none.
        """
        assert hasattr(view, 'get_queryset') \
            or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            assert queryset is not None, (
                '{}.get_queryset() returned None'.format(view.__class__.__name__)
            )
            return queryset
        return view.queryset

    def has_permission(self, request, view):
        # Workaround to ensure ACLPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)

        return all(perm(request.user)[0] for perm in perms)

    def has_object_permission(self, request, view, obj):
        # authentication checks have already executed via has_permission
        queryset = self._queryset(view)
        user = request.user

        perms = self.get_required_object_permissions(request.method, obj)

        if not all(perm(request.user)[0] for perm in perms):
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.get_required_object_permissions('GET', obj)
            if not read_perms(request.user)[0]:
                raise Http404

            # Has read permissions.
            return False

        return True

