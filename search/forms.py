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

from django.db.models import Q
from simple_search import BaseSearchForm

from users.models import User, School

class UserSearchForm(BaseSearchForm):
    class Meta:
        base_qs = User.objects
        search_fields = ('^name', 'description', 'specifications', '=id') 

        # assumes a fulltext index has been defined on the fields
        # 'name,description,specifications,id'
        fulltext_indexes = (
            ('name', 2), # name matches are weighted higher
            ('name,description,specifications,id', 1),
        )
