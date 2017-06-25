# Re2o un logiciel d'administration développé initiallement au rezometz. Il
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

from django.forms import ModelForm, Form, ValidationError
from django import forms
from .models import OptionalUser, OptionalMachine, GeneralOption
from django.db.models import Q

class EditUserOptionsForm(ModelForm):
    class Meta:
        model = OptionalUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditUserOptionsForm, self).__init__(*args, **kwargs)
        self.fields['is_tel_mandatory'].label = 'Exiger un numéro de téléphone'
        self.fields['user_solde'].label = 'Activation du solde pour les utilisateurs'

class EditMachineOptionsForm(ModelForm):
    class Meta:
        model = OptionalMachine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditMachineOptionsForm, self).__init__(*args, **kwargs)
        self.fields['password_machine'].label = "Possibilité d'attribuer un mot de passe par interface"
        self.fields['max_lambdauser_interfaces'].label = "Maximum d'interfaces autorisées pour un user normal"
        self.fields['max_lambdauser_aliases'].label = "Maximum d'alias dns autorisés pour un user normal"


class EditGeneralOptionsForm(ModelForm):
    class Meta:
        model = GeneralOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditGeneralOptionsForm, self).__init__(*args, **kwargs)
        self.fields['search_display_page'].label = 'Resultats affichés dans une recherche'
        self.fields['pagination_number'].label = 'Items par page, taille normale (ex users)'
        self.fields['pagination_large_number'].label = 'Items par page, taille élevée (machines)'
