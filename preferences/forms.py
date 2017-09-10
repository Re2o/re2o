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

from __future__ import unicode_literals

from django.forms import ModelForm, Form, ValidationError
from django import forms
from .models import OptionalUser, OptionalMachine, OptionalTopologie, GeneralOption, AssoOption, MailMessageOption, Service
from django.db.models import Q

class EditOptionalUserForm(ModelForm):
    class Meta:
        model = OptionalUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditOptionalUserForm, self).__init__(*args, **kwargs)
        self.fields['is_tel_mandatory'].label = 'Exiger un numéro de téléphone'
        self.fields['user_solde'].label = 'Activation du solde pour les utilisateurs'

class EditOptionalMachineForm(ModelForm):
    class Meta:
        model = OptionalMachine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditOptionalMachineForm, self).__init__(*args, **kwargs)
        self.fields['password_machine'].label = "Possibilité d'attribuer un mot de passe par interface"
        self.fields['max_lambdauser_interfaces'].label = "Maximum d'interfaces autorisées pour un user normal"
        self.fields['max_lambdauser_aliases'].label = "Maximum d'alias dns autorisés pour un user normal"

class EditOptionalTopologieForm(ModelForm):
    class Meta:
        model = OptionalTopologie
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditOptionalTopologieForm, self).__init__(*args, **kwargs)
        self.fields['vlan_decision_ok'].label = "Vlan où placer les machines après acceptation RADIUS"
        self.fields['vlan_decision_nok'].label = "Vlan où placer les machines après rejet RADIUS"

class EditGeneralOptionForm(ModelForm):
    class Meta:
        model = GeneralOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditGeneralOptionForm, self).__init__(*args, **kwargs)
        self.fields['search_display_page'].label = 'Resultats affichés dans une recherche'
        self.fields['pagination_number'].label = 'Items par page, taille normale (ex users)'
        self.fields['pagination_large_number'].label = 'Items par page, taille élevée (machines)'
        self.fields['req_expire_hrs'].label = 'Temps avant expiration du lien de reinitialisation de mot de passe (en heures)'
        self.fields['site_name'].label = 'Nom du site web'
        self.fields['email_from'].label = 'Adresse mail d\'expedition automatique'

class EditAssoOptionForm(ModelForm):
    class Meta:
        model = AssoOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditAssoOptionForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Nom de l\'asso'
        self.fields['siret'].label = 'SIRET'
        self.fields['adresse1'].label = 'Adresse (ligne 1)'
        self.fields['adresse2'].label = 'Adresse (ligne 2)'
        self.fields['contact'].label = 'Email de contact'
        self.fields['telephone'].label = 'Numéro de téléphone'
        self.fields['pseudo'].label = 'Pseudo d\'usage'
        self.fields['utilisateur_asso'].label = 'Compte utilisé pour faire les modifications depuis /admin'

class EditMailMessageOptionForm(ModelForm):
    class Meta:
        model = MailMessageOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditMailMessageOptionForm, self).__init__(*args, **kwargs)
        self.fields['welcome_mail_fr'].label = 'Message dans le mail de bienvenue en français'
        self.fields['welcome_mail_en'].label = 'Message dans le mail de bienvenue en anglais'

class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = '__all__'

class DelServiceForm(Form):
    services = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), label="Enregistrements service actuels",  widget=forms.CheckboxSelectMultiple)
