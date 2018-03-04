#!/usr/bin/env python3
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Matthieu Michelet
# Copyright © 2018  Gabriel Detraz
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
Write in a python file the list of all contributors sorted by number of commits.
This list is extracted from the FedeRez gitlab repository.
"""
fous moi un truc adapté au dessus aussi


from django.core.management.base import BaseCommand, CommandError
import os

class Command(BaseCommand):
    help = 'Update contributors list' 

    def handle(self, *args, **options):
        contributeurs = [item.split('\t')[1] for item in os.popen("git shortlog -s -n").read().split("\n") if '\t' in item]
        self.stdout.write(self.style.SUCCESS("Exportation Sucessfull"))
        contrib_file = open("contributors.py", "w")
        contrib_file.write("#!/usr/bin/env python3\n")
        contrib_file.write("\n")
        contrib_file.write("contributeurs = " + str(contributeurs))
