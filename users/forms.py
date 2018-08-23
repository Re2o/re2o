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
from django.utils.translation import ugettext_lazy as _

from preferences.models import OptionalUser
from re2o.utils import remove_user_room, get_input_formats_help_text
from re2o.mixins import FormRevMixin
from re2o.field_permissions import FieldPermissionFormMixin

from .widgets import DateTimePicker

from .models import (
    User,
    ServiceUser,
    School,
    ListRight,
    Whitelist,
    EMailAddress,
    ListShell,
    Ban,
    Adherent,
    Club
)


class PassForm(FormRevMixin, FieldPermissionFormMixin, forms.ModelForm):
    """Formulaire de changement de mot de passe. Verifie que les 2
    nouveaux mots de passe renseignés sont identiques et respectent
    une norme"""
    selfpasswd = forms.CharField(
        label=_("Current password"),
        max_length=255,
        widget=forms.PasswordInput
    )
    passwd1 = forms.CharField(
        label=_("New password"),
        max_length=255,
        validators=[MinLengthValidator(8)],
        widget=forms.PasswordInput
    )
    passwd2 = forms.CharField(
        label=_("New password confirmation"),
        max_length=255,
        validators=[MinLengthValidator(8)],
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = []

    def clean_passwd2(self):
        """Verifie que passwd1 et 2 sont identiques"""
        # Check that the two password entries match
        password1 = self.cleaned_data.get("passwd1")
        password2 = self.cleaned_data.get("passwd2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                _("The new passwords don't match.")
            )
        return password2

    def clean_selfpasswd(self):
        """Verifie si il y a lieu que le mdp self est correct"""
        if not self.instance.check_password(
                self.cleaned_data.get("selfpasswd")
            ):
            raise forms.ValidationError(_("The current password is incorrect."))
        return

    def save(self, commit=True):
        """Changement du mot de passe"""
        user = super(PassForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get("passwd1"))
        user.save()


class UserCreationForm(FormRevMixin, forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password.

    Formulaire pour la création d'un user. N'est utilisé que pour
    l'admin, lors de la creation d'un user par admin. Inclu tous les
    champs obligatoires"""
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        validators=[MinLengthValidator(8)],
        max_length=255
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        validators=[MinLengthValidator(8)],
        max_length=255
    )
    is_admin = forms.BooleanField(label=_("Is admin"))

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(UserCreationForm, self).__init__(*args, prefix=prefix, **kwargs)

    def clean_email(self):
        if not OptionalUser.objects.first().local_email_domain in self.cleaned_data.get('email'):
            return self.cleaned_data.get('email').lower()
        else:
            raise forms.ValidationError(_("You can't use an internal address"
                                          " as your external address."))

    class Meta:
        model = Adherent
        fields = ('pseudo', 'surname', 'email')

    def clean_password2(self):
        """Verifie que password1 et 2 sont identiques"""
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("The passwords don't match."))
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.save()
        user.is_admin = self.cleaned_data.get("is_admin")
        return user


class ServiceUserCreationForm(FormRevMixin, forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password.

    Formulaire pour la creation de nouveaux serviceusers.
    Requiert seulement un mot de passe; et un pseudo"""
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        min_length=8,
        max_length=255
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
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
            raise forms.ValidationError(_("The passwords don't match."))
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(ServiceUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.save()
        return user


class UserChangeForm(FormRevMixin, forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.

    Formulaire pour la modification d'un user coté admin
    """
    password = ReadOnlyPasswordHashField()
    is_admin = forms.BooleanField(label=_("Is admin"), required=False)

    class Meta:
        model = Adherent
        fields = ('pseudo', 'password', 'surname', 'email')

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(UserChangeForm, self).__init__(*args, prefix=prefix, **kwargs)
        print(_("User is admin: %s") % kwargs['instance'].is_admin)
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


class ServiceUserChangeForm(FormRevMixin, forms.ModelForm):
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
    pseudo = forms.CharField(label=_("Username"), max_length=255)
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
            if date > timezone.now():
                raise forms.ValidationError(_("Impossible to archive users"
                                              " whose end access date is in"
                                              " the future."))


class AdherentForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Formulaire de base d'edition d'un user. Formulaire de base, utilisé
    pour l'edition de self par self ou un cableur. On formate les champs
    avec des label plus jolis"""
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(AdherentForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = _("First name")
        self.fields['surname'].label = _("Surname")
        self.fields['email'].label = _("Email address")
        self.fields['school'].label = _("School")
        self.fields['comment'].label = _("Comment")
        self.fields['room'].label = _("Room")
        self.fields['room'].empty_label = _("No room")
        self.fields['school'].empty_label = _("Select a school")
        self.fields['gpg_fingerprint'].widget.attrs['placeholder'] = _("Leave empty if you don't have any GPG key.")
        if 'shell' in self.fields:
            self.fields['shell'].empty_label = _("Default shell")

    def clean_email(self):
        if not OptionalUser.objects.first().local_email_domain in self.cleaned_data.get('email'):
            return self.cleaned_data.get('email').lower()
        else:
            raise forms.ValidationError(
                    _("You can't use a {} address.").format(
                        OptionalUser.objects.first().local_email_domain))

    class Meta:
        model = Adherent
        fields = [
            'name',
            'surname',
            'pseudo',
            'email',
            'school',
            'comment',
            'telephone',
            'room',
            'shell',
            'gpg_fingerprint'
        ]


    def clean_telephone(self):
        """Verifie que le tel est présent si 'option est validée
        dans preferences"""
        telephone = self.cleaned_data['telephone']
        if not telephone and OptionalUser.get_cached_value('is_tel_mandatory'):
            raise forms.ValidationError(
                _("A valid telephone number is required.")
            )
        return telephone

    def clean_gpg_fingerprint(self):
        """Format the GPG fingerprint"""
        gpg_fingerprint = self.cleaned_data.get('gpg_fingerprint', None)
        if gpg_fingerprint:
            return gpg_fingerprint.replace(' ', '').upper()

    force = forms.BooleanField(
        label=_("Force the move?"),
        initial=False,
        required=False
    )

    def clean_force(self):
        """On supprime l'ancien user de la chambre si et seulement si la
        case est cochée"""
        if self.cleaned_data.get('force', False):
            remove_user_room(self.cleaned_data.get('room'))
        return


class ClubForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Formulaire de base d'edition d'un user. Formulaire de base, utilisé
    pour l'edition de self par self ou un cableur. On formate les champs
    avec des label plus jolis"""
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ClubForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['surname'].label = _("Name")
        self.fields['school'].label = _("School")
        self.fields['comment'].label = _("Comment")
        self.fields['room'].label = _("Room")
        self.fields['room'].empty_label = _("No room")
        self.fields['school'].empty_label = _("Select a school")
        self.fields['mailing'].label = _("Use a mailing list")

    class Meta:
        model = Club
        fields = [
            'surname',
            'pseudo',
            'school',
            'comment',
            'room',
            'telephone',
            'shell',
            'mailing'
        ]

    def clean_telephone(self):
        """Verifie que le tel est présent si 'option est validée
        dans preferences"""
        telephone = self.cleaned_data['telephone']
        if not telephone and OptionalUser.get_cached_value('is_tel_mandatory'):
            raise forms.ValidationError(
                _("A valid telephone number is required.")
            )
        return telephone


class ClubAdminandMembersForm(FormRevMixin, ModelForm):
    """Permet d'éditer la liste des membres et des administrateurs
    d'un club"""
    class Meta:
        model = Club
        fields = ['administrators', 'members']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ClubAdminandMembersForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )


class PasswordForm(FormRevMixin, ModelForm):
    """ Formulaire de changement brut de mot de passe.
    Ne pas utiliser sans traitement"""
    class Meta:
        model = User
        fields = ['password', 'pwd_ntlm']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(PasswordForm, self).__init__(*args, prefix=prefix, **kwargs)


class ServiceUserForm(FormRevMixin, ModelForm):
    """ Modification d'un service user"""
    password = forms.CharField(
        label=_("New password"),
        max_length=255,
        validators=[MinLengthValidator(8)],
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = ServiceUser
        fields = ('pseudo', 'access_group','comment')

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ServiceUserForm, self).__init__(*args, prefix=prefix, **kwargs)

    def save(self, commit=True):
        """Changement du mot de passe"""
        user = super(ServiceUserForm, self).save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data.get("password"))
        user.save()


class EditServiceUserForm(ServiceUserForm):
    """Formulaire d'edition de base d'un service user. Ne permet
    d'editer que son group d'acl et son commentaire"""
    class Meta(ServiceUserForm.Meta):
        fields = ['access_group', 'comment']


class StateForm(FormRevMixin, ModelForm):
    """ Changement de l'état d'un user"""
    class Meta:
        model = User
        fields = ['state']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(StateForm, self).__init__(*args, prefix=prefix, **kwargs)


class GroupForm(FieldPermissionFormMixin, FormRevMixin, ModelForm):
    """ Gestion des groupes d'un user"""
    groups = forms.ModelMultipleChoiceField(
        Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ['is_superuser', 'groups']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(GroupForm, self).__init__(*args, prefix=prefix, **kwargs)
        if 'is_superuser' in self.fields:
            self.fields['is_superuser'].label = _("Superuser")


class SchoolForm(FormRevMixin, ModelForm):
    """Edition, creation d'un école"""
    class Meta:
        model = School
        fields = ['name']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(SchoolForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = _("School")


class ShellForm(FormRevMixin, ModelForm):
    """Edition, creation d'un école"""
    class Meta:
        model = ListShell
        fields = ['shell']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ShellForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['shell'].label = _("Shell name")


class ListRightForm(FormRevMixin, ModelForm):
    """Edition, d'un groupe , équivalent à un droit
    Ne permet pas d'editer le gid, car il sert de primary key"""
    permissions = forms.ModelMultipleChoiceField(
        Permission.objects.all().select_related('content_type'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = ListRight
        fields = ('name', 'unix_name', 'critical', 'permissions', 'details')

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ListRightForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['unix_name'].label = _("Name of the group of rights")


class NewListRightForm(ListRightForm):
    """Ajout d'un groupe/list de droit """
    class Meta(ListRightForm.Meta):
        fields = ('name', 'unix_name', 'gid', 'critical', 'permissions',
                  'details')

    def __init__(self, *args, **kwargs):
        super(NewListRightForm, self).__init__(*args, **kwargs)
        self.fields['gid'].label = _("GID. Warning: this field must not be"
                                     " edited after creation.")


class DelListRightForm(Form):
    """Suppression d'un ou plusieurs groupes"""
    listrights = forms.ModelMultipleChoiceField(
        queryset=ListRight.objects.none(),
        label=_("Current groups of rights"),
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
        label=_("Current schools"),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelSchoolForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['schools'].queryset = instances
        else:
            self.fields['schools'].queryset = School.objects.all()


class BanForm(FormRevMixin, ModelForm):
    """Creation, edition d'un objet bannissement"""
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(BanForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['date_end'].label = _("End date")
        self.fields['date_end'].localize = False

    class Meta:
        model = Ban
        exclude = ['user']
        widgets = {'date_end':DateTimePicker}


class WhitelistForm(FormRevMixin, ModelForm):
    """Creation, edition d'un objet whitelist"""
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(WhitelistForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['date_end'].label = _("End date")
        self.fields['date_end'].localize = False

    class Meta:
        model = Whitelist
        exclude = ['user']
        widgets = {'date_end':DateTimePicker}


class EMailAddressForm(FormRevMixin, ModelForm):
    """Create and edit a local email address"""
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EMailAddressForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['local_part'].label = _("Local part of the email address")
        self.fields['local_part'].help_text = _("Can't contain @")

    def clean_local_part(self):
        return self.cleaned_data.get('local_part').lower()

    class Meta:
        model = EMailAddress
        exclude = ['user']


class EmailSettingsForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Edit email-related settings"""
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EmailSettingsForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['email'].label = _("Main email address")
        if 'local_email_redirect' in self.fields:
            self.fields['local_email_redirect'].label = _("Redirect local emails")
        if 'local_email_enabled' in self.fields:
            self.fields['local_email_enabled'].label = _("Use local emails")

    def clean_email(self):
        if not OptionalUser.objects.first().local_email_domain in self.cleaned_data.get('email'):
            return self.cleaned_data.get('email').lower()
        else:
            raise forms.ValidationError(
                    _("You can't use a {} address.").format(
                        OptionalUser.objects.first().local_email_domain))

    class Meta:
        model = User
        fields = ['email','local_email_enabled', 'local_email_redirect']

