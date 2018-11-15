# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Gabriel Détraz
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

# -*- coding: utf-8 -*-
"""
Regroupe les fonctions transversales utiles

Et non corrélées/dépendantes des autres applications
"""

import smtplib

from django.utils.translation import ugettext_lazy as _

from re2o.settings import EMAIL_HOST


def smtp_check(local_part):
    """Return True if the local_part is already taken
       False if available"""
    try:
        srv = smtplib.SMTP(EMAIL_HOST)
        srv.putcmd("vrfy", local_part)
        reply_code = srv.getreply()[0]
        srv.close()
        if reply_code in [250, 252]:
            return True, _("This domain is already taken")
    except:
        return True, _("Smtp unreachable")
    return False, None
