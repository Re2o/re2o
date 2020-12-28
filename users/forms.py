# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017-2020  Gabriel Détraz
# Copyright © 2017-2020  Lara Kermarec
# Copyright © 2017-2020  Augustin Lemesle
# Copyright © 2017-2020  Hugo Levy--Falk
# Copyright © 2017-2020  Jean-Romain Garnier
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
Forms for the 'users' app of re2o. It highly depends on
:users:models and is mainly used by :users:views.

The following forms are mainly used to create, edit or delete
anything related to 'users' :
    * Adherent (personnal data)
    * Club
    * Ban
    * ServiceUser
    * Whitelists
    * ...

See the details for each of these operations in the documentation
of each of the method.
"""

from __future__ import unicode_literals

from os import walk, path

from django import forms
from django.forms import ModelForm, Form
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password, password_validators_help_text_html
from django.core.validators import MinLengthValidator
from django.conf import settings
from django.utils import timezone
from django.utils.functional import lazy
from django.contrib.auth.models import Group, Permission
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from machines.models import Interface, Machine, Nas
from topologie.models import Port
from preferences.models import OptionalUser
from re2o.utils import remove_user_room
from re2o.base import get_input_formats_help_text
from re2o.mixins import FormRevMixin, AutocompleteMultipleModelMixin, AutocompleteModelMixin
from re2o.field_permissions import FieldPermissionFormMixin

from preferences.models import GeneralOption

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
    Club,
)


#### Django Admin Custom Views


class UserAdminForm(FormRevMixin, forms.ModelForm):
    """A form for creating new and editing users. Includes all the required
    fields, plus a repeated password.

    Parameters:
        DjangoForm : Inherit from basic django form
    """

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        max_length=255,
        help_text=password_validators_help_text_html(),
        required=False,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        max_length=255,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(UserAdminForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["email"].required = True

    class Meta:
        fields = ("pseudo", "surname", "name", "email", "is_superuser")

    def clean_password2(self):
        """Clean password 2, check if passwd1 and 2 values match.

        Parameters:
            self : Apply on a django Form UserCreationForm instance
            
        Returns:
            password2 (string): The password2 value if all tests returned True
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError(_("The passwords don't match."))
            validate_password(password1)
        return password2

    def save(self, commit=True):
        """Save function. Call standard "set_password" django function,
        from provided value for new password, for making hash.

        Parameters:
            self : Apply on a django Form UserCreationForm instance
            commit : If False, don't make the real save in database
        """
        # Save the provided password in hashed format
        user = super(UserAdminForm, self).save(commit=False)
        if self.cleaned_data["password1"]:
            user.set_password(self.cleaned_data["password1"])
            user.save()
        return user


class ServiceUserAdminForm(FormRevMixin, forms.ModelForm):
    """A form for creating new service users. Includes all the required
    fields, plus a repeated password. For Admin view purpose only.

    Parameters:
        DjangoForm : Inherit from basic django form
    """

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        max_length=255,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        max_length=255,
    )

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(ServiceUserAdminForm, self).__init__(*args, prefix=prefix, **kwargs)

    class Meta:
        model = ServiceUser
        fields = ("pseudo",)

    def clean_password2(self):
        """Clean password 2, check if passwd1 and 2 values match.

        Parameters:
            self : Apply on a django Form UserCreationForm instance
 
        Returns:
            password2 (string): The password2 value if all tests returned True
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("The passwords don't match."))
        return password2

    def save(self, commit=True):
        """Save function. Call standard "set_password" django function,
        from provided value for new password, for making hash. 

        Parameters:
            self : Apply on a django Form ServiceUserAdminForm instance
            commit : If False, don't make the real save in database
        """
        user = super(ServiceUserAdminForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.save()
        return user


### Classic Django View


class PassForm(FormRevMixin, FieldPermissionFormMixin, forms.ModelForm):
    """Django form for changing password, check if 2 passwords are the same,
    and validate password for django base password validators provided in
    settings_local.
    
    Parameters:
        DjangoForm : Inherit from basic django form
        
    """
    selfpasswd = forms.CharField(
        label=_("Current password"), max_length=255, widget=forms.PasswordInput
    )
    passwd1 = forms.CharField(
        label=_("New password"),
        max_length=255,
        widget=forms.PasswordInput,
        help_text=password_validators_help_text_html()
    )
    passwd2 = forms.CharField(
        label=_("New password confirmation"),
        max_length=255,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = []

    def clean_passwd2(self):
        """Clean password 2, check if passwd1 and 2 values match, and
        apply django validator with validate_password function. 
        
        Parameters:
            self : Apply on a django Form PassForm instance
            
        Returns:
            password2 (string): The password2 value if all tests returned True
        """
        password1 = self.cleaned_data.get("passwd1")
        password2 = self.cleaned_data.get("passwd2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("The new passwords don't match."))
        validate_password(password1, user=self.instance)
        return password2

    def clean_selfpasswd(self):
        """Clean selfpassword, check if provided original user password match
        with the stored value.

        Parameters:
            self : Apply on a django Form PassForm instance
        """
        if not self.instance.check_password(self.cleaned_data.get("selfpasswd")):
            raise forms.ValidationError(_("The current password is incorrect."))
        return

    def save(self, commit=True):
        """Save function. Call standard "set_password" django function,
        and call set_active for set user in active state if needed.

        Parameters:
            self : Apply on a django Form PassForm instance
            commit : If False, don't make the real save in database
        """
        user = super(PassForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get("passwd1"))
        user.save()


class ResetPasswordForm(forms.Form):
    """A form for asking to reset password. 

    Parameters:
        DjangoForm : Inherit from basic django form
    """    

    pseudo = forms.CharField(label=_("Username"), max_length=255)
    email = forms.EmailField(max_length=255)


class MassArchiveForm(forms.Form):
    """A form for archiving a lot de users. Get a start date
    for start archiving.

    Parameters:
        DjangoForm : Inherit from basic django form
    """   

    date = forms.DateTimeField(help_text="%d/%m/%y")
    full_archive = forms.BooleanField(
        label=_(
            "Fully archive users? WARNING: CRITICAL OPERATION IF TRUE"
        ),
        initial=False,
        required=False,
    )

    def clean(self):
        cleaned_data = super(MassArchiveForm, self).clean()
        date = cleaned_data.get("date")
        if date:
            if date > timezone.now():
                raise forms.ValidationError(
                    _(
                        "Impossible to archive users"
                        " whose end access date is in"
                        " the future."
                    )
                )


class AdherentForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Adherent Edition Form, base form used for editing user by himself
    or another user. Labels are provided for help purposes.

    Parameters:
        DjangoForm : Inherit from basic django form
    """   

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(AdherentForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["name"].label = _("First name")
        self.fields["surname"].label = _("Surname")
        self.fields["email"].label = _("Email address")
        self.fields["school"].label = _("School")
        self.fields["comment"].label = _("Comment")
        if "room" in self.fields:
            self.fields["room"].label = _("Room")
            self.fields["room"].empty_label = _("No room")
        self.fields["school"].empty_label = _("Select a school")

    class Meta:
        model = Adherent
        fields = [
            "name",
            "surname",
            "pseudo",
            "email",
            "school",
            "comment",
            "telephone",
            "room",
        ]
        widgets = {
            "school": AutocompleteModelMixin(
                url="/users/school-autocomplete",
            ),
            "room": AutocompleteModelMixin(
                url="/topologie/room-autocomplete",
                attrs = {
                    "data-minimum-input-length": 3   # Only trigger autocompletion after 3 characters have been typed
                }
            ),
            "shell": AutocompleteModelMixin(
                url="/users/shell-autocomplete",
            )
        }

    force = forms.BooleanField(
        label=_("Force the move?"), initial=False, required=False
    )

    def clean_telephone(self):
        """Clean telephone, check if telephone is made mandatory, and
        raise error if not provided
        
        Parameters:
            self : Apply on a django Form AdherentForm instance
            
        Returns:
            telephone (string): The telephone string if clean is True
        """
        telephone = self.cleaned_data["telephone"]
        if not telephone and OptionalUser.get_cached_value("is_tel_mandatory"):
            raise forms.ValidationError(_("A valid telephone number is required."))
        return telephone

    def clean_force(self):
        """Clean force, remove previous user from room if needed.

        Parameters:
            self : Apply on a django Form AdherentForm instance
        """
        room = self.cleaned_data.get("room")
        if self.cleaned_data.get("force", False) and room:
            remove_user_room(room)
        return

    def clean_room(self):
        """Clean room, based on room policy provided by preferences.
        If needed, call remove_user_room to make the room empty before
        saving self.instance into that room.
        
        Parameters:
            self : Apply on a django Form AdherentForm instance
            
        Returns:
            room (string): The room instance
        """
        # Handle case where regular users can force move
        room = self.cleaned_data.get("room")
        room_policy = OptionalUser.get_cached_value("self_room_policy")
        if room_policy == OptionalUser.DISABLED or not room:
            return room

        # Remove the previous user's room, if allowed and necessary
        remove_user_room(room, force=bool(room_policy == OptionalUser.ALL_ROOM))

        # Run standard clean process
        return room


class AdherentCreationForm(AdherentForm):
    """AdherentCreationForm. Inherit from AdherentForm, base form used for creating
    user by himself or another user. Labels are provided for help purposes.
    Add some instructions, and validation for initial creation.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 
    # Champ pour choisir si un lien est envoyé par mail pour le mot de passe
    init_password_by_mail_info = _(
        "If this options is set, you will receive a link to set"
        " your initial password by email. If you do not have"
        " any means of accessing your emails, you can disable"
        " this option to set your password immediatly."
        " You will still receive an email to confirm your address."
        " Failure to confirm your address will result in an"
        " automatic suspension of your account until you do."
    )

    init_password_by_mail = forms.BooleanField(
        help_text=init_password_by_mail_info,
        required=False,
        initial=True
    )
    init_password_by_mail.label = _("Send password reset link by email.")

    # Champs pour initialiser le mot de passe
    # Validators are handled manually since theses fields aren't always required
    password1 = forms.CharField(
        required=False,
        label=_("Password"),
        widget=forms.PasswordInput,
        max_length=255,
        help_text=password_validators_help_text_html()
    )
    password2 = forms.CharField(
        required=False,
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        max_length=255,
    )

    # Champ permettant d'éviter au maxium les doublons d'utilisateurs
    former_user_check_info = _(
        "If you already have an account, please use it. If your lost access to"
        " it, please consider using the forgotten password button on the"
        " login page or contacting support."
    )
    former_user_check = forms.BooleanField(
        required=True, help_text=former_user_check_info
    )
    former_user_check.label = _("I certify that I have not had an account before.")

    # Checkbox for GTU
    gtu_check = forms.BooleanField(required=True)

    class Meta(AdherentForm.Meta):
        model = Adherent
        fields = [
            "name",
            "surname",
            "pseudo",
            "email",
            "school",
            "comment",
            "telephone",
            "room",
            "state",
        ]

    def __init__(self, *args, **kwargs):
        super(AdherentCreationForm, self).__init__(*args, **kwargs)
        gtu_file = GeneralOption.get_cached_value("GTU")
        self.fields["email"].required = True
        self.fields["gtu_check"].label = mark_safe(
            "%s <a href='%s' download='CGU'>%s</a>."
            % (
                _("I commit to accept the"),
                gtu_file.url if gtu_file else "#",
                _("General Terms of Use"),
            )
        )

        # Remove password fields if option is disabled
        if not OptionalUser.get_cached_value("allow_set_password_during_user_creation"):
            self.fields.pop("init_password_by_mail")
            self.fields.pop("password1")
            self.fields.pop("password2")

    def clean_password2(self):
        """Clean password 2, check if passwd1 and 2 values match, and
        apply django validator with validate_password function. 

        Parameters:
            self : Apply on a django Form AdherentCreationForm instance
            
        Returns:
            password2 (string): The password2 value if all tests returned True
        """
        send_email = self.cleaned_data.get("init_password_by_mail")
        if send_email:
            return None

        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("The passwords don't match."))
        validate_password(password1)
        return password2

    def save(self, commit=True):
        """Save function. If password has been set during creation, 
        call standard "set_password" django function from provided value
        for new password, for making hash.

        Parameters:
            self : Apply on a django Form AdherentCreationForm instance
            commit : If False, don't make the real save in database
        """
        # Save the provided password in hashed format
        user = super(AdherentForm, self).save(commit=False)

        is_set_password_allowed = OptionalUser.get_cached_value("allow_set_password_during_user_creation")
        set_passwd = is_set_password_allowed and not self.cleaned_data.get("init_password_by_mail")
        if set_passwd:
            user.set_password(self.cleaned_data["password1"])

        user.save()
        return user


class AdherentEditForm(AdherentForm):
    """AdherentEditForm. Inherit from AdherentForm, base form used for editing
    user by himself or another user. Labels are provided for help purposes.
    Add some instructions, and validation, fields depends on editing user rights.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    def __init__(self, *args, **kwargs):
        super(AdherentEditForm, self).__init__(*args, **kwargs)
        self.fields["gpg_fingerprint"].widget.attrs["placeholder"] = _(
            "Leave empty if you don't have any GPG key."
        )
        self.user = kwargs["instance"]
        self.fields["email"].required = bool(self.user.email)
        if "shell" in self.fields:
            self.fields["shell"].empty_label = _("Default shell")

    class Meta(AdherentForm.Meta):
        model = Adherent
        fields = [
            "name",
            "surname",
            "pseudo",
            "email",
            "school",
            "comment",
            "telephone",
            "room",
            "shell",
            "gpg_fingerprint",
            "shortcuts_enabled",
        ]


class ClubForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """ClubForm. For editing club by himself or another user. Labels are provided for
    help purposes. Add some instructions, and validation, fields depends 
    on editing user rights.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(ClubForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["surname"].label = _("Name")
        self.fields["school"].label = _("School")
        self.fields["comment"].label = _("Comment")
        self.fields["email"].label = _("Email address")
        if "room" in self.fields:
            self.fields["room"].label = _("Room")
            self.fields["room"].empty_label = _("No room")
        self.fields["school"].empty_label = _("Select a school")
        self.fields["mailing"].label = _("Use a mailing list")

    class Meta:
        model = Club
        fields = [
            "surname",
            "pseudo",
            "school",
            "comment",
            "room",
            "email",
            "telephone",
            "email",
            "shell",
            "mailing",
        ]
        widgets = {
            "school": AutocompleteModelMixin(
                url="/users/school-autocomplete",
            ),
            "room": AutocompleteModelMixin(
                url="/topologie/room-autocomplete",
            ),
            "shell": AutocompleteModelMixin(
                url="/users/shell-autocomplete",
            )
        }

    def clean_telephone(self):
        """Clean telephone, check if telephone is made mandatory, and
        raise error if not provided
        
        Parameters:
            self : Apply on a django Form ClubForm instance
            
        Returns:
            telephone (string): The telephone string if clean is True
        """
        telephone = self.cleaned_data["telephone"]
        if not telephone and OptionalUser.get_cached_value("is_tel_mandatory"):
            raise forms.ValidationError(_("A valid telephone number is required."))
        return telephone


class ClubAdminandMembersForm(FormRevMixin, ModelForm):
    """ClubAdminandMembersForm. Only For editing administrators of a club by himself
    or another user.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    class Meta:
        model = Club
        fields = ["administrators", "members"]
        widgets = {
            "administrators": AutocompleteMultipleModelMixin(
                url="/users/adherent-autocomplete",
            ),
            "members": AutocompleteMultipleModelMixin(
                url="/users/adherent-autocomplete",
            )
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(ClubAdminandMembersForm, self).__init__(*args, prefix=prefix, **kwargs)


class PasswordForm(FormRevMixin, ModelForm):
    """PasswordForm. Do not use directly in views without extra validations.
    
    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    class Meta:
        model = User
        fields = ["password", "pwd_ntlm"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(PasswordForm, self).__init__(*args, prefix=prefix, **kwargs)


class ServiceUserForm(FormRevMixin, ModelForm):
    """ServiceUserForm, used for creating a service user, require
    a password and set it.
    
    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    password = forms.CharField(
        label=_("New password"),
        max_length=255,
        validators=[MinLengthValidator(8)],
        widget=forms.PasswordInput,
        required=True,
    )

    class Meta:
        model = ServiceUser
        fields = ("pseudo", "access_group", "comment")

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(ServiceUserForm, self).__init__(*args, prefix=prefix, **kwargs)

    def save(self, commit=True):
        """Save function. If password has been changed and provided, 
        call standard "set_password" django function from provided value
        for new password, for making hash.

        Parameters:
            self : Apply on a django Form ServiceUserForm instance
            commit : If False, don't make the real save in database
        """
        user = super(ServiceUserForm, self).save(commit=False)
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data.get("password"))
        user.save()


class EditServiceUserForm(ServiceUserForm):
    """EditServiceUserForm, used for editing a service user, can
    edit password, access_group and comment.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    password = forms.CharField(
        label=_("New password"),
        max_length=255,
        validators=[MinLengthValidator(8)],
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta(ServiceUserForm.Meta):
        fields = ["access_group", "comment"]


class StateForm(FormRevMixin, ModelForm):
    """StateForm, Change state of an user, and if
    its main email is verified or not

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    class Meta:
        model = User
        fields = ["state", "email_state"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(StateForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["state"].label = _("State")
        self.fields["email_state"].label = _("Email state")


class GroupForm(FieldPermissionFormMixin, FormRevMixin, ModelForm):
    """GroupForm, form used for editing user groups.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    groups = forms.ModelMultipleChoiceField(
        Group.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )

    class Meta:
        model = User
        fields = ["is_superuser", "groups"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(GroupForm, self).__init__(*args, prefix=prefix, **kwargs)
        if "is_superuser" in self.fields:
            self.fields["is_superuser"].label = _("Superuser")


class SchoolForm(FormRevMixin, ModelForm):
    """SchoolForm, form used for creating or editing school.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    class Meta:
        model = School
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(SchoolForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["name"].label = _("School")


class ShellForm(FormRevMixin, ModelForm):
    """ShellForm, form used for creating or editing shell.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    class Meta:
        model = ListShell
        fields = ["shell"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(ShellForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["shell"].label = _("Shell name")


class ListRightForm(FormRevMixin, ModelForm):
    """ListRightForm, form used for editing a listright,
    related with django group object. Gid, primary key, can't
    be edited.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    permissions = forms.ModelMultipleChoiceField(
        Permission.objects.all().select_related("content_type"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = ListRight
        fields = ("name", "unix_name", "critical", "permissions", "details")

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(ListRightForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["unix_name"].label = _("Name of the group of rights")


class NewListRightForm(ListRightForm):
    """ListRightForm, form used for creating a listright,
    related with django group object.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    class Meta(ListRightForm.Meta):
        fields = ("name", "unix_name", "gid", "critical", "permissions", "details")

    def __init__(self, *args, **kwargs):
        super(NewListRightForm, self).__init__(*args, **kwargs)
        self.fields["gid"].label = _(
            "GID. Warning: this field must not be edited after creation."
        )


class DelListRightForm(Form):
    """DelListRightForm, form for deleting one or several ListRight
    instances.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    listrights = forms.ModelMultipleChoiceField(
        queryset=ListRight.objects.none(),
        label=_("Current groups of rights"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelListRightForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["listrights"].queryset = instances
        else:
            self.fields["listrights"].queryset = ListRight.objects.all()


class DelSchoolForm(Form):
    """DelSchoolForm, form for deleting one or several School
    instances.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    schools = forms.ModelMultipleChoiceField(
        queryset=School.objects.none(),
        label=_("Current schools"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelSchoolForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["schools"].queryset = instances
        else:
            self.fields["schools"].queryset = School.objects.all()


class BanForm(FormRevMixin, ModelForm):
    """BanForm, form used for creating or editing a ban instance.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(BanForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["date_end"].label = _("End date")
        self.fields["date_end"].localize = False

    class Meta:
        model = Ban
        exclude = ["user"]
        widgets = {"date_end": DateTimePicker}


class WhitelistForm(FormRevMixin, ModelForm):
    """WhitelistForm, form used for creating or editing a whitelist instance.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(WhitelistForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["date_end"].label = _("End date")
        self.fields["date_end"].localize = False

    class Meta:
        model = Whitelist
        exclude = ["user"]
        widgets = {"date_end": DateTimePicker}


class EMailAddressForm(FormRevMixin, ModelForm):
    """EMailAddressForm, form used for creating or editing a local
    email for a user.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EMailAddressForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["local_part"].label = _("Local part of the email address")
        self.fields["local_part"].help_text = _("Can't contain @.")

    def clean_local_part(self):
        return self.cleaned_data.get("local_part").lower()

    class Meta:
        model = EMailAddress
        exclude = ["user"]


class EmailSettingsForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """EMailSettingsForm, form used for editing email settings for a user.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EmailSettingsForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.user = kwargs["instance"]
        self.fields["email"].label = _("Main email address")
        self.fields["email"].required = bool(self.user.email)
        if "local_email_redirect" in self.fields:
            self.fields["local_email_redirect"].label = _("Redirect local emails")
        if "local_email_enabled" in self.fields:
            self.fields["local_email_enabled"].label = _("Use local emails")

    class Meta:
        model = User
        fields = ["email", "local_email_enabled", "local_email_redirect"]


class InitialRegisterForm(forms.Form):
    """InitialRegisterForm, form used for auto-register of room and mac-address
    with captive-portal.

    Parameters:
        DjangoForm : Inherit from basic django form
    """ 
    register_room = forms.BooleanField(required=False)
    register_machine = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        switch_ip = kwargs.pop("switch_ip")
        switch_port = kwargs.pop("switch_port")
        client_mac = kwargs.pop("client_mac")
        self.user = kwargs.pop("user")
        if switch_ip and switch_port:
            # Looking for a port
            port = Port.objects.filter(
                switch__interface__ipv4__ipv4=switch_ip, port=switch_port
            ).first()
            # If a port exists, checking there is a room AND radius
            if port:
                if (
                    port.get_port_profile.radius_type != "NO"
                    and port.get_port_profile.radius_mode == "STRICT"
                    and hasattr(port, "room")
                ):
                    # Requesting user is not in this room ?
                    if self.user.room != port.room:
                        self.new_room = port.room
        if client_mac and switch_ip:
            # If this interface doesn't already exists
            if not Interface.objects.filter(mac_address=client_mac):
                self.mac_address = client_mac
                self.nas_type = Nas.objects.filter(
                    nas_type__interface__ipv4__ipv4=switch_ip
                ).first()
        super(InitialRegisterForm, self).__init__(*args, **kwargs)
        if hasattr(self, "new_room"):
            self.fields["register_room"].label = _("This room is my room")
        else:
            self.fields.pop("register_room")
        if hasattr(self, "mac_address"):
            self.fields["register_machine"].label = _(
                "This new connected device is mine"
            )
        else:
            self.fields.pop("register_machine")

    def clean_register_room(self):
        """Clean room, call remove_user_room to make the room empty before
        saving self.instance into that room.
        
        Parameters:
            self : Apply on a django Form InitialRegisterForm instance
            
        """
        if self.cleaned_data["register_room"]:
            if self.user.is_class_adherent:
                remove_user_room(self.new_room)
                user = self.user.adherent
                user.room = self.new_room
                user.save()
            if self.user.is_class_club:
                user = self.user.club
                user.room = self.new_room
                user.save()

    def clean_register_machine(self):
        """Clean register room, autoregister machine from user request mac_address.

        Parameters:
            self : Apply on a django Form InitialRegisterForm instance
            
        """
        if self.cleaned_data["register_machine"]:
            if self.mac_address and self.nas_type:
                self.user.autoregister_machine(self.mac_address, self.nas_type)


class ThemeForm(FormRevMixin, forms.Form):
    """Form to change the theme of a user.
    """

    theme = forms.ChoiceField(widget=forms.Select())

    def __init__(self, *args, **kwargs):
        _, _ ,themes = next(walk(path.join(settings.STATIC_ROOT, "css/themes")))
        if not themes:
            themes = ["default.css"]
        super(ThemeForm, self).__init__(*args, **kwargs)
        self.fields['theme'].choices = [(theme, theme) for theme in themes]
