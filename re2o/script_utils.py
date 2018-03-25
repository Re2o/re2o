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

import os, sys, pwd

proj_path="/var/www/re2o"
os.environ.setdefault("DJANGO_SETTINGS_MODULE","re2o.settings")
sys.path.append(proj_path)
os.chdir(proj_path)
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


from django.core.management.base import CommandError
from users.models import User

def get_user(pseudo):
    """Cherche un utilisateur re2o à partir de son pseudo"""
    user = User.objects.filter(pseudo=pseudo)
    if len(user)==0:
        raise CommandError("Utilisateur invalide")
    if len(user)>1:
        raise CommandError("Plusieurs utilisateurs correspondant à ce pseudo. Ceci NE DEVRAIT PAS arriver")
    return user[0]

