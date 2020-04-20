# -*- mode: python; coding: utf-8 -*-
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

"""Defines the serializers of the API
"""

from rest_framework import serializers

import preferences.models as preferences
import users.models as users

# The namespace used for the API. It must match the namespace used in the
# urlpatterns to include the API URLs.
API_NAMESPACE = "api"


class NamespacedHRField(serializers.HyperlinkedRelatedField):
    """A `rest_framework.serializers.HyperlinkedRelatedField` subclass to
    automatically prefix view names with the API namespace.
    """

    def __init__(self, view_name=None, **kwargs):
        if view_name is not None:
            view_name = "%s:%s" % (API_NAMESPACE, view_name)
        super(NamespacedHRField, self).__init__(view_name=view_name, **kwargs)


class NamespacedHIField(serializers.HyperlinkedIdentityField):
    """A `rest_framework.serializers.HyperlinkedIdentityField` subclass to
    automatically prefix view names with teh API namespace.
    """

    def __init__(self, view_name=None, **kwargs):
        if view_name is not None:
            view_name = "%s:%s" % (API_NAMESPACE, view_name)
        super(NamespacedHIField, self).__init__(view_name=view_name, **kwargs)


class NamespacedHMSerializer(serializers.HyperlinkedModelSerializer):
    """A `rest_framework.serializers.HyperlinkedModelSerializer` subclass to
    automatically prefix view names with the API namespace.
    """

    serializer_related_field = NamespacedHRField
    serializer_url_field = NamespacedHIField



class ReminderUsersSerializer(UserSerializer):
    """Serialize the data about a mailing member.
    """

    class Meta(UserSerializer.Meta):
        fields = ("get_full_name", "get_mail")


class ReminderSerializer(serializers.ModelSerializer):
    """
    Serialize the data about a reminder
    """

    users_to_remind = ReminderUsersSerializer(many=True)

    class Meta:
        model = preferences.Reminder
        fields = ("days", "message", "users_to_remind")


