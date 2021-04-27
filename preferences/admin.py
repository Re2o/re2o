# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
# Copyright © 2017  Augustin Lemesle
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
Admin classes for models of preferences app.
"""
from __future__ import unicode_literals

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import (AssoOption, DocumentTemplate, GeneralOption, HomeOption,
                     MailContact, MailMessageOption, Mandate, OptionalMachine,
                     OptionalTopologie, OptionalUser, RadiusKey, Reminder,
                     Service, SwitchManagementCred)


class OptionalUserAdmin(VersionAdmin):
    """Admin class for user options."""

    pass


class OptionalTopologieAdmin(VersionAdmin):
    """Admin class for topology options."""

    pass


class OptionalMachineAdmin(VersionAdmin):
    """Admin class for machines options."""

    pass


class GeneralOptionAdmin(VersionAdmin):
    """Admin class for general options."""

    pass


class ServiceAdmin(VersionAdmin):
    """Admin class for services (on the homepage)."""

    pass


class MailContactAdmin(VersionAdmin):
    """Admin class for contact email addresses."""

    pass


class AssoOptionAdmin(VersionAdmin):
    """Admin class for organisation options."""

    pass


class MailMessageOptionAdmin(VersionAdmin):
    """Admin class for email messages options."""

    pass


class HomeOptionAdmin(VersionAdmin):
    """Admin class for home options."""

    pass


class RadiusKeyAdmin(VersionAdmin):
    """Admin class for RADIUS keys options."""

    pass


class SwitchManagementCredAdmin(VersionAdmin):
    """Admin class for switch management credentials options."""

    pass


class ReminderAdmin(VersionAdmin):
    """Admin class for reminder options."""

    pass


class DocumentTemplateAdmin(VersionAdmin):
    """Admin class for document templates."""

    pass


class MandateAdmin(VersionAdmin):
    """Admin class for mandates."""

    pass


admin.site.register(OptionalUser, OptionalUserAdmin)
admin.site.register(OptionalMachine, OptionalMachineAdmin)
admin.site.register(OptionalTopologie, OptionalTopologieAdmin)
admin.site.register(GeneralOption, GeneralOptionAdmin)
admin.site.register(HomeOption, HomeOptionAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(MailContact, MailContactAdmin)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(RadiusKey, RadiusKeyAdmin)
admin.site.register(SwitchManagementCred, SwitchManagementCredAdmin)
admin.site.register(AssoOption, AssoOptionAdmin)
admin.site.register(MailMessageOption, MailMessageOptionAdmin)
admin.site.register(DocumentTemplate, DocumentTemplateAdmin)
admin.site.register(Mandate, MandateAdmin)
