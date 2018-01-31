# -*- mode: python; coding: utf-8 -*-
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
"""
Definition des forms pour l'application users.

Modification, creation de :
    - un user (informations personnelles)
    - un bannissement
    - le mot de passe d'un user
    - une whiteliste
    - un user de service
"""

from __future__ import unicode_literals

from django import forms
from django.forms import ModelForm, Form
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.contrib.auth.models import Group, Permission

from preferences.models import OptionalUser
from .models import User, ServiceUser, School, ListRight, Whitelist
from .models import Ban, Adherent, Club
from re2o.utils import remove_user_room

from re2o.field_permissions import FieldPermissionFormMixin

NOW = timezone.now()


class PassForm(forms.Form):
    """Formulaire de changement de mot de passe. Verifie que les 2
    nouveaux mots de passe renseignés sont identiques et respectent
    une norme"""
    passwd1 = forms.CharField(
        label=u'Nouveau mot de passe',
        max_length=255,
        validators=[MinLengthValidator(8)],
        widget=forms.PasswordInput
    )
    passwd2 = forms.CharField(
        label=u'Saisir à nouveau le mot de passe',
        max_length=255,
        validators=[MinLengthValidator(8)],
        widget=forms.PasswordInput
    )

    def clean_passwd2(self):
        """Verifie que passwd1 et 2 sont identiques"""
        # Check that the two password entries match
        password1 = self.cleaned_data.get("passwd1")
        password2 = self.cleaned_data.get("passwd2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password.

    Formulaire pour la création d'un user. N'est utilisé que pour
    l'admin, lors de la creation d'un user par admin. Inclu tous les
    champs obligatoires"""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        validators=[MinLengthValidator(8)],
        max_length=255
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput,
        validators=[MinLengthValidator(8)],
        max_length=255
    )
    is_admin = forms.BooleanField(label='is admin')

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(UserCreationForm, self).__init__(*args, prefix=prefix, **kwargs)

    class Meta:
        model = Adherent
        fields = ('pseudo', 'surname', 'email')

    def clean_password2(self):
        """Verifie que password1 et 2 sont identiques"""
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.save()
        user.is_admin = self.cleaned_data.get("is_admin")
        return user


class ServiceUserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password.

    Formulaire pour la creation de nouveaux serviceusers.
    Requiert seulement un mot de passe; et un pseudo"""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        min_length=8,
        max_length=255
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput,
        min_length=8,
        max_length=255
    )

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ServiceUserCreationForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )

    class Meta:
        model = ServiceUser
        fields = ('pseudo',)

    def clean_password2(self):
        """Verifie que password1 et 2 sont indentiques"""
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(ServiceUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.

    Formulaire pour la modification d'un user coté admin
    """
    password = ReadOnlyPasswordHashField()
    is_admin = forms.BooleanField(label='is admin', required=False)

    class Meta:
        model = Adherent
        fields = ('pseudo', 'password', 'surname', 'email')

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(UserChangeForm, self).__init__(*args, prefix=prefix, **kwargs)
        print("User is admin : %s" % kwargs['instance'].is_admin)
        self.initial['is_admin'] = kwargs['instance'].is_admin

    def clean_password(self):
        """Dummy fun"""
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserChangeForm, self).save(commit=False)
        user.is_admin = self.cleaned_data.get("is_admin")
        if commit:
            user.save()
        return user


class ServiceUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.

    Formulaire pour l'edition des service users coté admin
    """
    password = ReadOnlyPasswordHashField()

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ServiceUserChangeForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )

    class Meta:
        model = ServiceUser
        fields = ('pseudo',)

    def clean_password(self):
        """Dummy fun"""
        return self.initial["password"]


class ResetPasswordForm(forms.Form):
    """Formulaire de demande de reinitialisation de mot de passe,
    mdp oublié"""
    pseudo = forms.CharField(label=u'Pseudo', max_length=255)
    email = forms.EmailField(max_length=255)


class MassArchiveForm(forms.Form):
    """Formulaire d'archivage des users inactif. Prend en argument
    du formulaire la date de depart avant laquelle archiver les
    users"""
    date = forms.DateTimeField(help_text='%d/%m/%y')

    def clean(self):
        cleaned_data = super(MassArchiveForm, self).clean()
        date = cleaned_data.get("date")
        if date:
            if date > NOW:
                raise forms.ValidationError("Impossible d'archiver des\
                utilisateurs dont la fin d'accès se situe dans le futur !")


class AdherentForm(FieldPermissionFormMixin, ModelForm):
    """Formulaire de base d'edition d'un user. Formulaire de base, utilisé
    pour l'edition de self par self ou un cableur. On formate les champs
    avec des label plus jolis"""
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(AdherentForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = 'Prénom'
        self.fields['surname'].label = 'Nom'
        self.fields['school'].label = 'Établissement'
        self.fields['comment'].label = 'Commentaire'
        self.fields['room'].label = 'Chambre'
        self.fields['room'].empty_label = "Pas de chambre"
        self.fields['school'].empty_label = "Séléctionner un établissement"

    class Meta:
        model = Adherent
        fields = [
            'name',
            'surname',
            'pseudo',
            'email',
            'school',
            'comment',
            'room',
            'shell',
            'telephone',
        ]

    def clean_telephone(self):
        """Verifie que le tel est présent si 'option est validée
        dans preferences"""
        telephone = self.cleaned_data['telephone']
        if not telephone and OptionalUser.get_cached_value('is_tel_mandatory'):
            raise forms.ValidationError(
                "Un numéro de téléphone valide est requis"
            )
        return telephone

    force = forms.BooleanField(
        label="Forcer le déménagement ?",
        initial=False,
        required=False
    )

    def clean_force(self):
        """On supprime l'ancien user de la chambre si et seulement si la
        case est cochée"""
        if self.cleaned_data.get('force', False):
            remove_user_room(self.cleaned_data.get('room'))
        return


class ClubForm(FieldPermissionFormMixin, ModelForm):
    """Formulaire de base d'edition d'un user. Formulaire de base, utilisé
    pour l'edition de self par self ou un cableur. On formate les champs
    avec des label plus jolis"""
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ClubForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['surname'].label = 'Nom'
        self.fields['school'].label = 'Établissement'
        self.fields['comment'].label = 'Commentaire'
        self.fields['room'].label = 'Local'
        self.fields['room'].empty_label = "Pas de chambre"
        self.fields['school'].empty_label = "Séléctionner un établissement"

    class Meta:
        model = Club
        fields = [
            'surname',
            'pseudo',
            'email',
            'school',
            'comment',
            'room',
            'telephone',
            'shell',
        ]

    def clean_telephone(self):
        """Verifie que le tel est présent si 'option est validée
        dans preferences"""
        telephone = self.cleaned_data['telephone']
        if not telephone and OptionalUser.get_cached_value('is_tel_mandatory'):
            raise forms.ValidationError(
                "Un numéro de téléphone valide est requis"
            )
        return telephone


class ClubAdminandMembersForm(ModelForm):
    """Permet d'éditer la liste des membres et des administrateurs
    d'un club"""
    class Meta:
        model = Club
        fields = ['administrators', 'members']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ClubAdminandMembersForm, self).__init__(*args, prefix=prefix, **kwargs)


class PasswordForm(ModelForm):
    """ Formulaire de changement brut de mot de passe.
    Ne pas utiliser sans traitement"""
    class Meta:
        model = User
        fields = ['password', 'pwd_ntlm']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(PasswordForm, self).__init__(*args, prefix=prefix, **kwargs)


class ServiceUserForm(ModelForm):
    """ Modification d'un service user"""
    password = forms.CharField(
        label=u'Nouveau mot de passe',
        max_length=255,
        validators=[MinLengthValidator(8)],
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = ServiceUser
        fields = ('pseudo', 'access_group')

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ServiceUserForm, self).__init__(*args, prefix=prefix, **kwargs)


class EditServiceUserForm(ServiceUserForm):
    """Formulaire d'edition de base d'un service user. Ne permet
    d'editer que son group d'acl et son commentaire"""
    class Meta(ServiceUserForm.Meta):
        fields = ['access_group', 'comment']


class StateForm(ModelForm):
    """ Changement de l'état d'un user"""
    class Meta:
        model = User
        fields = ['state']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(StateForm, self).__init__(*args, prefix=prefix, **kwargs)


class GroupForm(ModelForm):
    """ Gestion des groupes d'un user"""
    groups = forms.ModelMultipleChoiceField(
        Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ['groups']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(GroupForm, self).__init__(*args, prefix=prefix, **kwargs)


class SchoolForm(ModelForm):
    """Edition, creation d'un école"""
    class Meta:
        model = School
        fields = ['name']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(SchoolForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = 'Établissement'


class ListRightForm(ModelForm):
    """Edition, d'un groupe , équivalent à un droit
    Ne peremet pas d'editer le gid, car il sert de primary key"""
    permissions = forms.ModelMultipleChoiceField(
        Permission.objects.all().select_related('content_type'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = ListRight
        fields = ['name', 'unix_name', 'critical', 'permissions', 'details']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ListRightForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['unix_name'].label = 'Nom du droit/groupe'


class NewListRightForm(ListRightForm):
    """Ajout d'un groupe/list de droit """
    class Meta(ListRightForm.Meta):
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(NewListRightForm, self).__init__(*args, **kwargs)
        self.fields['gid'].label = 'Gid, attention, cet attribut ne doit\
        pas être modifié après création'


class DelListRightForm(Form):
    """Suppression d'un ou plusieurs groupes"""
    listrights = forms.ModelMultipleChoiceField(
        queryset=ListRight.objects.none(),
        label="Droits actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelListRightForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['listrights'].queryset = instances
        else:
            self.fields['listrights'].queryset = ListRight.objects.all()


class DelSchoolForm(Form):
    """Suppression d'une ou plusieurs écoles"""
    schools = forms.ModelMultipleChoiceField(
        queryset=School.objects.none(),
        label="Etablissements actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelSchoolForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['schools'].queryset = instances
        else:
            self.fields['schools'].queryset = School.objects.all()


class BanForm(ModelForm):
    """Creation, edition d'un objet bannissement"""
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(BanForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['date_end'].label = 'Date de fin'

    class Meta:
        model = Ban
        exclude = ['user']


class WhitelistForm(ModelForm):
    """Creation, edition d'un objet whitelist"""
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(WhitelistForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['date_end'].label = 'Date de fin'

    class Meta:
        model = Whitelist
        exclude = ['user']
