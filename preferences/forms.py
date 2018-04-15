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
"""
Formulaire d'edition des réglages : user, machine, topologie, asso...
"""

from __future__ import unicode_literals

from django.forms import ModelForm, Form
from django import forms
from .models import OptionalUser, OptionalMachine, OptionalTopologie
from .models import GeneralOption, AssoOption, MailMessageOption, Service


class EditOptionalUserForm(ModelForm):
    """Formulaire d'édition des options de l'user. (solde, telephone..)"""
    class Meta:
        model = OptionalUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditOptionalUserForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['is_tel_mandatory'].label = (
            'Exiger un numéro de téléphone'
        )
        self.fields['user_solde'].label = (
            'Activation du solde pour les utilisateurs'
        )
        self.fields['max_solde'].label = 'Solde maximum'
        self.fields['min_online_payment'].label = (
            'Montant de rechargement minimum en ligne'
        )
        self.fields['self_adhesion'].label = 'Auto inscription'


class EditOptionalMachineForm(ModelForm):
    """Options machines (max de machines, etc)"""
    class Meta:
        model = OptionalMachine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditOptionalMachineForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['password_machine'].label = "Possibilité d'attribuer\
        un mot de passe par interface"
        self.fields['max_lambdauser_interfaces'].label = "Maximum\
        d'interfaces autorisées pour un user normal"
        self.fields['max_lambdauser_aliases'].label = "Maximum d'alias\
        dns autorisés pour un user normal"


class EditOptionalTopologieForm(ModelForm):
    """Options de topologie, formulaire d'edition (vlan par default etc)"""
    class Meta:
        model = OptionalTopologie
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditOptionalTopologieForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['vlan_decision_ok'].label = "Vlan où placer les\
        machines après acceptation RADIUS"
        self.fields['vlan_decision_nok'].label = "Vlan où placer les\
        machines après rejet RADIUS"


class EditGeneralOptionForm(ModelForm):
    """Options générales (affichages de résultats de recherche, etc)"""
    class Meta:
        model = GeneralOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditGeneralOptionForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['search_display_page'].label = 'Resultats\
        affichés dans une recherche'
        self.fields['pagination_number'].label = 'Items par page,\
        taille normale (ex users)'
        self.fields['pagination_large_number'].label = 'Items par page,\
        taille élevée (machines)'
        self.fields['req_expire_hrs'].label = 'Temps avant expiration du lien\
        de reinitialisation de mot de passe (en heures)'
        self.fields['site_name'].label = 'Nom du site web'
        self.fields['email_from'].label = "Adresse mail d\
        'expedition automatique"
        self.fields['GTU_sum_up'].label = "Résumé des CGU"


class EditAssoOptionForm(ModelForm):
    """Options de l'asso (addresse, telephone, etc)"""
    class Meta:
        model = AssoOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditAssoOptionForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['name'].label = 'Nom de l\'asso'
        self.fields['siret'].label = 'SIRET'
        self.fields['adresse1'].label = 'Adresse (ligne 1)'
        self.fields['adresse2'].label = 'Adresse (ligne 2)'
        self.fields['contact'].label = 'Email de contact'
        self.fields['telephone'].label = 'Numéro de téléphone'
        self.fields['pseudo'].label = 'Pseudo d\'usage'
        self.fields['utilisateur_asso'].label = 'Compte utilisé pour\
        faire les modifications depuis /admin'

    def clean(self):
        cleaned_data = super().clean()
        payment = cleaned_data.get('payment')

        if payment == 'NONE':
            return cleaned_data

        if not cleaned_data.get('payment_id', ''):
            msg = forms.ValidationError("Vous devez spécifier un identifiant \
                                        de paiement.")
            self.add_error('payment_id', msg)
        if not cleaned_data.get('payment_pass', ''):
            msg = forms.ValidationError("Vous devez spécifier un mot de passe \
                                        de paiement.")
            self.add_error('payment_pass', msg)

        return cleaned_data


class EditMailMessageOptionForm(ModelForm):
    """Formulaire d'edition des messages de bienvenue personnalisés"""
    class Meta:
        model = MailMessageOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditMailMessageOptionForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['welcome_mail_fr'].label = 'Message dans le\
        mail de bienvenue en français'
        self.fields['welcome_mail_en'].label = 'Message dans le\
        mail de bienvenue en anglais'


class ServiceForm(ModelForm):
    """Edition, ajout de services sur la page d'accueil"""
    class Meta:
        model = Service
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ServiceForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelServiceForm(Form):
    """Suppression de services sur la page d'accueil"""
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.none(),
        label="Enregistrements service actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelServiceForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['services'].queryset = instances
        else:
            self.fields['services'].queryset = Service.objects.all()
