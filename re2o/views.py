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

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.context_processors import csrf
from django.template import Context, RequestContext, loader
from re2o.settings import services_urls

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render(request, template, c)


def index(request):
    i = 0
    services = [{}]
    for key, s in services_urls.items():
        if len(services) <= i:
            services += [{}]
        services[i][key] = s
        i = i + 1 if i < 2 else 0

    return form({'services_urls': services}, 're2o/index.html', request)
