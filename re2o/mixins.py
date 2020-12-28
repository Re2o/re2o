# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Gabriel Détraz
# Copyright © 2017  Charlie Jacomme
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
"""re2o.mixins
A set of mixins used all over the project to avoid duplicating code
"""

from reversion import revisions as reversion
from django.db import transaction
from django.utils.translation import ugettext as _


class RevMixin(object):
    """A mixin to subclass the save and delete function of a model
    to enforce the versioning of the object before those actions
    really happen"""

    def save(self, *args, **kwargs):
        """ Creates a version of this object and save it to database """
        if self.pk is None:
            with transaction.atomic(), reversion.create_revision():
                reversion.set_comment("Creation")
                return super(RevMixin, self).save(*args, **kwargs)
        return super(RevMixin, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Creates a version of this object and delete it from database """
        with transaction.atomic(), reversion.create_revision():
            reversion.set_comment("Deletion")
            return super(RevMixin, self).delete(*args, **kwargs)


class FormRevMixin(object):
    """A mixin to subclass the save function of a form
    to enforce the versionning of the object before it is really edited"""

    def save(self, *args, **kwargs):
        """ Create a version of this object and save it to database """
        if reversion.get_comment() != "" and self.changed_data != []:
            reversion.set_comment(
                reversion.get_comment()
                + ",%s" % ", ".join(field for field in self.changed_data)
            )
        elif self.changed_data:
            reversion.set_comment(
                "Field(s) edited: %s" % ", ".join(field for field in self.changed_data)
            )
        return super(FormRevMixin, self).save(*args, **kwargs)


class AclMixin(object):
    """This mixin is used in nearly every class/models defined in re2o apps.
    It is used by acl, in models (decorators can_...) and in templates tags
    :get_instance: Applied on a class, take an id argument, return an instance
    :can_create: Applied on a class, take the requested user, return if the
        user can do the creation
    :can_edit: Applied on an instance, return if the user can edit the
        instance
    :can_delete: Applied on an instance, return if the user can delete the
        instance
    :can_view: Applied on an instance, return if the user can view the
        instance
    :can_view_all: Applied on a class, return if the user can view all
        instances"""

    @classmethod
    def get_classname(cls):
        """ Returns the name of the class where this mixin is used """
        return str(cls.__name__).lower()

    @classmethod
    def get_modulename(cls):
        """ Returns the name of the module where this mixin is used """
        return str(cls.__module__).split(".")[0].lower()

    @classmethod
    def get_instance(cls, object_id, *_args, **kwargs):
        """Get an instance from its id.

        Parameters:
           object_id (int): Id of the instance to find

        Returns:
           Django instance: Instance of this class
        """
        return cls.objects.get(pk=object_id)

    @classmethod
    def can_create(cls, user_request, *_args, **_kwargs):
        """Check if a user has the right to create an object

        Parameters:
            user_request: User calling for this action

        Returns:
            Boolean: True if user_request has the right access to do it, else
            false with reason for reject authorization
        """
        permission = cls.get_modulename() + ".add_" + cls.get_classname()
        can = user_request.has_perm(permission)
        return (
            can,
            _("You don't have the right to create a %s object.") % cls.get_classname()
            if not can
            else None,
            (permission,),
        )

    def can_edit(self, user_request, *_args, **_kwargs):
        """Check if a user has the right to edit an instance

        Parameters:
            user_request: User calling for this action
            self: Instance to edit

        Returns:
            Boolean: True if user_request has the right access to do it, else
            false with reason for reject authorization
        """
        permission = self.get_modulename() + ".change_" + self.get_classname()
        can = user_request.has_perm(permission)
        return (
            can,
            _("You don't have the right to edit a %s object.") % self.get_classname()
            if not can
            else None,
            (permission,),
        )

    def can_delete(self, user_request, *_args, **_kwargs):
        """Check if a user has the right to delete an instance

        Parameters:
            user_request: User calling for this action
            self: Instance to delete

        Returns:
            Boolean: True if user_request has the right access to do it, else
            false with reason for reject authorization
        """
        permission = self.get_modulename() + ".delete_" + self.get_classname()
        can = user_request.has_perm(permission)
        return (
            can,
            _("You don't have the right to delete a %s object.") % self.get_classname()
            if not can
            else None,
            (permission,),
        )

    @classmethod
    def can_view_all(cls, user_request, *_args, **_kwargs):
        """Check if a user can view all instances of an object

        Parameters:
            user_request: User calling for this action

        Returns:
            Boolean: True if user_request has the right access to do it, else
            false with reason for reject authorization
        """
        permission = cls.get_modulename() + ".view_" + cls.get_classname()
        can = user_request.has_perm(permission)
        return (
            can,
            _("You don't have the right to view every %s object.") % cls.get_classname()
            if not can
            else None,
            (permission,),
        )

    @classmethod
    def can_edit_all(cls, user_request, *_args, **_kwargs):
        """Check if a user can edit all instances of an object

        Parameters:
            user_request: User calling for this action

        Returns:
            Boolean: True if user_request has the right access to do it, else
            false with reason for reject authorization
        """
        permission = cls.get_modulename() + ".change_" + cls.get_classname()
        can = user_request.has_perm(permission)
        return (
            can,
            _("You don't have the right to edit every %s object.") % cls.get_classname()
            if not can
            else None,
            (permission,),
        )

    def can_view(self, user_request, *_args, **_kwargs):
        """Check if a user can view an instance of an object

        Parameters:
            user_request: User calling for this action
            self: Instance to view

        Returns:
            Boolean: True if user_request has the right access to do it, else
            false with reason for reject authorization
        """
        permission = self.get_modulename() + ".view_" + self.get_classname()
        can = user_request.has_perm(permission)
        return (
            can,
            _("You don't have the right to view a %s object.") % self.get_classname()
            if not can
            else None,
            (permission,),
        )
