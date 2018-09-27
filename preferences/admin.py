# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
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
Classes admin pour les models de preferences
"""
from __future__ import unicode_literals

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import (
    OptionalUser,
    OptionalMachine,
    OptionalTopologie,
    GeneralOption,
    Service,
    MailContact,
    AssoOption,
    MailMessageOption,
    HomeOption,
    RadiusKey,
    SwitchManagementCred,
    Reminder
)


class OptionalUserAdmin(VersionAdmin):
    """Class admin options user"""
    pass


class OptionalTopologieAdmin(VersionAdmin):
    """Class admin options topologie"""
    pass


class OptionalMachineAdmin(VersionAdmin):
    """Class admin options machines"""
    pass


class GeneralOptionAdmin(VersionAdmin):
    """Class admin options générales"""
    pass


class ServiceAdmin(VersionAdmin):
    """Class admin gestion des services de la page d'accueil"""
    pass


class MailContactAdmin(VersionAdmin):
    """Admin class for contact email adresses"""
    pass


class AssoOptionAdmin(VersionAdmin):
    """Class admin options de l'asso"""
    pass


class MailMessageOptionAdmin(VersionAdmin):
    """Class admin options mail"""
    pass


class HomeOptionAdmin(VersionAdmin):
    """Class admin options home"""
    pass


class RadiusKeyAdmin(VersionAdmin):
    """Class radiuskey"""
    pass

class SwitchManagementCredAdmin(VersionAdmin):
    """Class managementcred for switch"""
    pass

class ReminderAdmin(VersionAdmin):
    """Class reminder for switch"""
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
