# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2020  Jean-Romain Garnier
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
# Jean-Romain Garnier
"""
Regroupe les fonctions en lien avec les mails
"""

from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail as django_send_mail
from django.contrib import messages
from smtplib import SMTPException


def send_mail(request, *args, **kwargs):
    """Wrapper for Django's send_mail which handles errors"""
    try:
        kwargs["fail_silently"] = request is None
        django_send_mail(*args, **kwargs)
    except (SMTPException, ConnectionError) as e:
        messages.error(
            request,
            _("Failed to send email: %(error)s.") % {
                "error": e,
            },
        )


def send_mail_object(mail, request):
    """Wrapper for Django's EmailMessage.send which handles errors"""
    try:
        mail.send()
    except (SMTPException, ConnectionError) as e:
        if request:
            messages.error(
                request,
                _("Failed to send email: %(error)s.") % {
                    "error": e,
                },
            )
