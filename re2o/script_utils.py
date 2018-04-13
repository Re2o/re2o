# ⁻*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
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

import os
import sys
import pwd

from django.core.wsgi import get_wsgi_application

from django.core.management.base import CommandError
from users.models import User

from django.utils.html import strip_tags
from reversion import revisions as reversion
from django.db import transaction
from getpass import getpass

proj_path = "/var/www/re2o"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re2o.settings")
sys.path.append(proj_path)
os.chdir(proj_path)

application = get_wsgi_application()


def get_user(pseudo):
    """Cherche un utilisateur re2o à partir de son pseudo"""
    user = User.objects.filter(pseudo=pseudo)
    if len(user) == 0:
        raise CommandError("Utilisateur invalide")
    if len(user) > 1:
        raise CommandError("Plusieurs utilisateurs correspondant à ce "
                           "pseudo. Ceci NE DEVRAIT PAS arriver")
    return user[0]


def get_system_user():
    """Retourne l'utilisateur système ayant lancé la commande"""
    return pwd.getpwuid(int(os.getenv("SUDO_UID") or os.getuid())).pw_name


def form_cli(Form, user, action, *args, **kwargs):
    """
    Remplit un formulaire à partir de la ligne de commande
        Form : le formulaire (sous forme de classe) à remplir
        user : l'utilisateur re2o faisant la modification
        action : l'action réalisée par le formulaire (pour les logs)
    Les arguments suivants sont transmis tels quels au formulaire.
    """
    data = {}
    dumb_form = Form(user=user, *args, **kwargs)
    for key in dumb_form.fields:
        if not dumb_form.fields[key].widget.input_type == 'hidden':
            if dumb_form.fields[key].widget.input_type == 'password':
                data[key] = getpass("%s : " % dumb_form.fields[key].label)
            else:
                data[key] = input("%s : " % dumb_form.fields[key].label)

    form = Form(data, user=user, *args, **kwargs)
    if not form.is_valid():
        sys.stderr.write("Erreurs : \n")
        for err in form.errors:
            # Oui, oui, on gère du HTML là où d'autres ont eu la
            # lumineuse idée de le mettre
            sys.stderr.write(
                "\t%s : %s\n" % (err, strip_tags(form.errors[err]))
            )
        raise CommandError("Formulaire invalide")

    with transaction.atomic(), reversion.create_revision():
        form.save()
        reversion.set_user(user)
        reversion.set_comment(action)

    sys.stdout.write("%s : effectué. La modification peut prendre "
                     "quelques minutes pour s'appliquer.\n" % action)
