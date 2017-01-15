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

# -*- coding: utf-8 -*-


from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.validators import MinLengthValidator

from .models import User, ServiceUser, get_admin_right

class PassForm(forms.Form):
    passwd1 = forms.CharField(label=u'Nouveau mot de passe', max_length=255, validators=[MinLengthValidator(8)], widget=forms.PasswordInput)
    passwd2 = forms.CharField(label=u'Saisir à nouveau le mot de passe', max_length=255, validators=[MinLengthValidator(8)], widget=forms.PasswordInput)


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, validators=[MinLengthValidator(8)], max_length=255)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, validators=[MinLengthValidator(8)], max_length=255)
    is_admin = forms.BooleanField(label='is admin')

    class Meta:
        model = User
        fields = ('pseudo', 'name', 'surname', 'email')

    def clean_password2(self):
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
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, min_length=8, max_length=255)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, min_length=8, max_length=255)

    class Meta:
        model = ServiceUser
        fields = ('pseudo',)

    def clean_password2(self):
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
    """
    password = ReadOnlyPasswordHashField()
    is_admin = forms.BooleanField(label='is admin', required=False)

    class Meta:
        model = User
        fields = ('pseudo', 'password', 'name', 'surname', 'email')

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        print("User is admin : %s" % kwargs['instance'].is_admin)
        self.initial['is_admin'] = kwargs['instance'].is_admin

    def clean_password(self):
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
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = ServiceUser
        fields = ('pseudo',)

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class ResetPasswordForm(forms.Form):
    pseudo = forms.CharField(label=u'Pseudo', max_length=255)
    email = forms.EmailField(max_length=255)
