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
from re2o.mixins import FormRevMixin

from django.forms import ModelForm, Form
from django import forms
from django.utils.translation import ugettext_lazy as _
from re2o.mixins import FormRevMixin
from .models import (
    OptionalUser,
    OptionalMachine,
    OptionalTopologie,
    GeneralOption,
    AssoOption,
    MailMessageOption,
    HomeOption,
    Service,
    MailContact
    Reminder
)


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
            _("Telephone number required")
        )
        self.fields['gpg_fingerprint'].label = _("GPG fingerprint")
        self.fields['all_can_create_club'].label = _("All can create a club")
        self.fields['all_can_create_adherent'].label = _("All can create a member")
        self.fields['self_adhesion'].label = _("Self registration")
        self.fields['shell_default'].label = _("Default shell")


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
        self.fields['password_machine'].label = _("Possibility to set a"
                                                  " password per machine")
        self.fields['max_lambdauser_interfaces'].label = _("Maximum number of"
                                                           " interfaces"
                                                           " allowed for a"
                                                           " standard user")
        self.fields['max_lambdauser_aliases'].label = _("Maximum number of DNS"
                                                        " aliases allowed for"
                                                        " a standard user")
        self.fields['ipv6_mode'].label = _("IPv6 mode")
        self.fields['create_machine'].label = _("Can create a machine")


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
        self.fields['radius_general_policy'].label = _("RADIUS general policy")
        self.fields['vlan_decision_ok'].label = _("VLAN for machines accepted"
                                                  " by RADIUS")
        self.fields['vlan_decision_nok'].label = _("VLAN for machines rejected"
                                                   " by RADIUS")


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
        self.fields['general_message_fr'].label = _("General message in French")
        self.fields['general_message_en'].label = _("General message in English")
        self.fields['search_display_page'].label = _("Number of results"
                                                     " displayed when"
                                                     " searching")
        self.fields['pagination_number'].label = _("Number of items per page,"
                                                   " standard size (e.g."
                                                   " users)")
        self.fields['pagination_large_number'].label = _("Number of items per"
                                                         " page, large size"
                                                         " (e.g. machines)")
        self.fields['req_expire_hrs'].label = _("Time before expiration of the"
                                                " reset password link (in"
                                                " hours)")
        self.fields['site_name'].label = _("Website name")
        self.fields['email_from'].label = _("Email address for automatic"
                                            " emailing")
        self.fields['GTU_sum_up'].label = _("Summary of the General Terms of"
                                            " Use")
        self.fields['GTU'].label = _("General Terms of Use")


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
        self.fields['name'].label = _("Organisation name")
        self.fields['siret'].label = _("SIRET number")
        self.fields['adresse1'].label = _("Address (line 1)")
        self.fields['adresse2'].label = _("Address (line 2)")
        self.fields['contact'].label = _("Contact email address")
        self.fields['telephone'].label = _("Telephone number")
        self.fields['pseudo'].label = _("Usual name")
        self.fields['utilisateur_asso'].label = _("Account used for editing"
                                                  " from /admin")
        self.fields['payment'].label = _("Payment")
        self.fields['payment_id'].label = _("Payment ID")
        self.fields['payment_pass'].label = _("Payment password")
        self.fields['description'].label = _("Description")


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
        self.fields['welcome_mail_fr'].label = _("Message for the French"
                                                 " welcome email")
        self.fields['welcome_mail_en'].label = _("Message for the English"
                                                 " welcome email")


class EditHomeOptionForm(ModelForm):
    """Edition forms of Home options"""
    class Meta:
        model = HomeOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditHomeOptionForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['facebook_url'].label = _("Facebook URL")
        self.fields['twitter_url'].label = _("Twitter URL")
        self.fields['twitter_account_name'].label = _("Twitter account name")


class ServiceForm(FormRevMixin, ModelForm):
    """Edition, ajout de services sur la page d'accueil"""
    class Meta:
        model = Service
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ServiceForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = _("Name")
        self.fields['url'].label = _("URL")
        self.fields['description'].label = _("Description")
        self.fields['image'].label = _("Image")



class DelServiceForm(Form):
    """Suppression de services sur la page d'accueil"""
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.none(),
        label=_("Current services"),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelServiceForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['services'].queryset = instances
        else:
            self.fields['services'].queryset = Service.objects.all()

class MailContactForm(FormRevMixin, ModelForm):
    """Edit and add contact email adress"""
    class Meta:
        model = MailContact
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(MailContactForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelMailContactForm(Form):
    """Delete contact email adress"""
    mailcontacts = forms.ModelMultipleChoiceField(
        queryset=MailContact.objects.none(),
        label="Enregistrements adresses actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelMailContactForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['mailcontacts'].queryset = instances
        else:
            self.fields['mailcontacts'].queryset = MailContact.objects.all()

class ReminderForm(FormRevMixin, ModelForm):
    """Edition, ajout de rappel"""
    class Meta:
        model = Reminder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ReminderForm, self).__init__(*args, prefix=prefix, **kwargs)

class ReminderForm(FormRevMixin, ModelForm):
    """Edition, ajout de rappel"""
    class Meta:
        model = Reminder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ReminderForm, self).__init__(*args, prefix=prefix, **kwargs)


