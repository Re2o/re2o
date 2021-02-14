# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Arthur Grisel-Davy
# Copyright © 2020  Gabriel Détraz
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
Multi_op model
"""

from __future__ import absolute_import

from django.core.mail import EmailMessage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import loader
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from reversion.models import Version

import users.models
from preferences.models import GeneralOption
from re2o.mail_utils import send_mail_object
from re2o.mixins import AclMixin

from .preferences.models import MultiopOption
