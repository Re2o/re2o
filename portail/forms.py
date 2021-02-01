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

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from cotisations.models import Article, Paiement
from re2o.widgets import AutocompleteModelWidget
from users.models import Adherent


class AdherentForm(UserCreationForm):
    # Champ permettant d'éviter au maximum les doublons d'utilisateurs
    former_user_check = forms.BooleanField(
        label=_("I certify that I have not had an account before."),
        required=True,
        help_text=_("If you already have an account, please use it. If your lost access to "
                    "it, please consider using the forgotten password button on the "
                    "login page or contacting support.")
    )

    class Meta:
        model = Adherent
        fields = ("name", "surname", "pseudo", "email", "telephone", "password1", "password2", "room", "school",
                  "former_user_check",)
        widgets = {
            "school": AutocompleteModelWidget(url="/users/school-autocomplete"),
            "room": AutocompleteModelWidget(
                url="/topologie/room-autocomplete",
                attrs={
                    "data-minimum-input-length": 3  # Only trigger autocompletion after 3 characters have been typed
                },
            ),
        }


class MembershipForm(forms.Form):
    payment_method = forms.ModelChoiceField(
        Paiement.objects.filter(available_for_everyone=True),
    )

    article = forms.ModelChoiceField(
        Article.objects.filter(Q(duration_connection__gt=0) | Q(duration_days_connection__gt=0),
                               available_for_everyone=True,
                               need_membership=False),
    )
