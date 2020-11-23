# ⁻*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Benjamin Graillot
# Copyright © 2013-2015 Raphaël-David Lasseri <lasseri@crans.org>
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

import sys
import re
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import make_aware

from users.models import User

# Une liste d'expressions régulières à chercher dans les logs.
# Elles doivent contenir un groupe 'date' et un groupe 'user'.
# Pour le CAS on prend comme entrée
# cat ~/cas.log | grep -B 2 -A 2 "ACTION: AUTHENTICATION_SUCCESS"| grep 'WHEN\|WHO'|sed 'N;s/\n/ /'
COMPILED_REGEX = map(
    re.compile,
    [
        r"^(?P<date>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}).*(?:"
        r"dovecot.*Login: user=<|"
        r"sshd.*Accepted.*for "
        r")(?P<user>[^ >]+).*$",
        r"^(?P<date>.*) LOGIN INFO User logged in : (?P<user>.*)",
        r"WHO: \[username: (?P<user>.*)\] WHEN: (?P<date>.* CET .*)",
        r"WHO: \[username: (?P<user>.*)\] WHEN: (?P<date>.* CEST .*)",
    ],
)

# Les formats de date en strftime associés aux expressions ci-dessus.
DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%d/%b/%Y:%H:%M:%S",
    "%a %b %d CET %H:%M:%S%Y",
    "%a %b %d CEST %H:%M:%S%Y",
]


class Command(BaseCommand):
    help = (
        "Update the time of the latest connection for users by matching"
        " stdin against a set of regular expressions."
    )

    def handle(self, *args, **options):
        def parse_logs(logfile):
            """
            Parse les logs sur l'entrée standard et rempli un dictionnaire
            ayant pour clef le pseudo de l'adherent
            """
            global COMPILED_REGEX, DATE_FORMATS

            parsed_log = {}
            for line in logfile:
                for i, regex in enumerate(COMPILED_REGEX):
                    m = regex.match(line)
                    if m:
                        parsed_log[m.group("user")] = make_aware(
                            datetime.strptime(m.group("date"), DATE_FORMATS[i])
                        )
            return parsed_log

        parsed_log = parse_logs(sys.stdin)

        for pseudo in parsed_log:
            for user in User.objects.filter(pseudo=pseudo):
                last_login = parsed_log.get(user.pseudo, user.last_login)
                if not user.last_login:
                    user.last_login = last_login
                elif last_login > user.last_login:
                    user.last_login = last_login
                user.save()
