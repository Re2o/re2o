# ⁻*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Lev-Arcady Sellem
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
"""re2o.script_utils
A set of utility scripts that can be used as standalone to interact easily
with Re2o throught the CLI
"""

import os
import pwd
import sys
from getpass import getpass
from os.path import dirname

from django.core.management.base import CommandError
from django.core.wsgi import get_wsgi_application
from django.db import transaction
from django.utils.html import strip_tags
from reversion import revisions as reversion

from users.models import User

proj_path = dirname(dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re2o.settings")
sys.path.append(proj_path)
os.chdir(proj_path)

application = get_wsgi_application()


def get_user(pseudo):
    """Find a user from its pseudo

    Parameters:
        pseudo (string): pseudo of this user

    Returns:
        user instance:Instance of user

    """
    user = User.objects.filter(pseudo=pseudo)
    if len(user) == 0:
        raise CommandError("Invalid user.")
    if len(user) > 1:
        raise CommandError("Several users match this username. This SHOULD NOT happen.")
    return user[0]


def get_system_user():
    """Find the system user login who used the command"""
    return pwd.getpwuid(int(os.getenv("SUDO_UID") or os.getuid())).pw_name


def form_cli(Form, user, action, *args, **kwargs):
    """
    Fill-in a django form from cli

    Parameters
        Form : a django class form to fill-in
        user : a re2o user doign the modification
        action: the action done with that form, for logs purpose

    """
    data = {}
    dumb_form = Form(user=user, *args, **kwargs)
    for key in dumb_form.fields:
        if not dumb_form.fields[key].widget.input_type == "hidden":
            if dumb_form.fields[key].widget.input_type == "password":
                data[key] = getpass("%s : " % dumb_form.fields[key].label)
            else:
                data[key] = input("%s : " % dumb_form.fields[key].label)

    form = Form(data, user=user, *args, **kwargs)
    if not form.is_valid():
        sys.stderr.write("Errors: \n")
        for err in form.errors:
            # Oui, oui, on gère du HTML là où d'autres ont eu la
            # lumineuse idée de le mettre
            sys.stderr.write("\t%s : %s\n" % (err, strip_tags(form.errors[err])))
        raise CommandError("Invalid form.")

    with transaction.atomic(), reversion.create_revision():
        form.save()
        reversion.set_user(user)
        reversion.set_comment(action)

    sys.stdout.write("%s: done. The edit may take several minutes to apply.\n" % action)
