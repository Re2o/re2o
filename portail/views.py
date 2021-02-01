# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Gabriel Détraz
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

from django.contrib.auth import login
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import AdherentForm


class SignUpView(CreateView):
    form_class = AdherentForm
    template_name = "portail/signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    @transaction.atomic
    def form_valid(self, form):
        ret = super().form_valid(form)
        login(self.request, form.instance)
        return ret

    def get_success_url(self):
        return reverse_lazy("users:profil", args=(self.object.pk,))
