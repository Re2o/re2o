# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
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

# App de gestion des users pour re2o
# Lara Kermarec, Gabriel Détraz, Lemesle Augustin
# Gplv2
"""
Django users views module.

Here are defined all functions of views, for the users re2o application. This views
allow both edition, creation, deletion and diplay of users objects.
Here are view that allow the addition/deletion/edition of:
    * Users (Club/Adherent) and derived settings like EmailSettings of users
    * School
    * Bans
    * Whitelist
    * Shell
    * ServiceUser

Also add extra views for :
    * Ask for reset password by email
    * Ask for new email for email confirmation
    * Register room and interface on user account with switch web redirection.

All the view must be as simple as possible, with returning the correct form to user during
get, and during post, performing change in database with simple ".save()" function.

The aim is to put all "intelligent" functions in both forms and models functions. In fact, this
will allow to user other frontend (like REST api) to perform editions, creations, etc on database,
without code duplication.

"""

from __future__ import unicode_literals

from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError, Count, Max
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from django.template import loader

from rest_framework.renderers import JSONRenderer
from reversion import revisions as reversion

from cotisations.models import Facture, Paiement
from machines.models import Machine

from preferences.models import OptionalUser, GeneralOption, AssoOption
from importlib import import_module
from django.conf import settings
from re2o.settings import LOCAL_APPS, OPTIONNAL_APPS_RE2O
from re2o.views import form
from re2o.utils import all_has_access, permission_tree
from re2o.base import re2o_paginator, SortTable
from re2o.acl import (
    can_create,
    can_edit,
    can_delete_set,
    can_delete,
    can_view,
    can_view_all,
    can_change,
)
from cotisations.utils import find_payment_method
from topologie.models import Port
from .models import (
    User,
    Ban,
    Whitelist,
    School,
    ListRight,
    Request,
    ServiceUser,
    Adherent,
    Club,
    ListShell,
    EMailAddress,
)
from .forms import (
    BanForm,
    WhitelistForm,
    EMailAddressForm,
    EmailSettingsForm,
    DelSchoolForm,
    DelListRightForm,
    NewListRightForm,
    StateForm,
    SchoolForm,
    ShellForm,
    EditServiceUserForm,
    ServiceUserForm,
    ListRightForm,
    AdherentCreationForm,
    AdherentEditForm,
    ClubForm,
    MassArchiveForm,
    PassForm,
    ResetPasswordForm,
    ClubAdminandMembersForm,
    GroupForm,
    InitialRegisterForm,
)

import os

@can_create(Adherent)
def new_user(request):
    """View for new Adherent/User form creation.
    Then, send an email to the new user, and also if needed to
    set its password.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django User form.

    """
    user = AdherentCreationForm(request.POST or None, request.FILES or None, user=request.user)
    user.request = request

    GTU_sum_up = GeneralOption.get_cached_value("GTU_sum_up")
    GTU = GeneralOption.get_cached_value("GTU")
    is_set_password_allowed = OptionalUser.get_cached_value(
        "allow_set_password_during_user_creation"
    )

    if user.is_valid():
        user = user.save()

        if user.password:
            user.send_confirm_email_if_necessary(request)
            messages.success(
                request,
                _("The user %s was created, a confirmation email was sent.")
                % user.pseudo,
            )
        else:
            user.reset_passwd_mail(request)
            messages.success(
                request,
                _("The user %s was created, an email to set the password was sent.")
                % user.pseudo,
            )

        return redirect(reverse("users:profil", kwargs={"userid": str(user.id)}))

    # Anonymous users are allowed to create new accounts
    # but they should be treated differently
    params = {
        "userform": user,
        "GTU_sum_up": GTU_sum_up,
        "GTU": GTU,
        "showCGU": True,
        "action_name": _("Commit"),
    }

    if is_set_password_allowed:
        params["load_js_file"] = "/static/js/toggle_password_fields.js"

    return form(params, "users/user.html", request)


@login_required
@can_create(Club)
def new_club(request):
    """View for new Club/User form creation.
    Then, send an email to the new user, and also if needed to
    set its password.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django User form.

    """
    club = ClubForm(request.POST or None, request.FILES or None, user=request.user)
    club.request = request

    if club.is_valid():
        club = club.save(commit=False)
        club.save()
        club.reset_passwd_mail(request)
        messages.success(
            request,
            _("The club %s was created, an email to set the password was sent.")
            % club.pseudo,
        )
        return redirect(reverse("users:profil", kwargs={"userid": str(club.id)}))
    return form(
        {"userform": club, "showCGU": False, "action_name": _("Create a club")},
        "users/user.html",
        request,
    )


@login_required
@can_edit(Club)
def edit_club_admin_members(request, club_instance, **_kwargs):
    """View for editing clubs and administrators.

    Parameters:
        request (django request): Standard django request.
        club_instance: Club instance to edit

    Returns:
        Django User form.

    """
    club = ClubAdminandMembersForm(request.POST or None, request.FILES or None, instance=club_instance)
    if club.is_valid():
        if club.changed_data:
            club.save()
            messages.success(request, _("The club was edited."))
        return redirect(
            reverse("users:profil", kwargs={"userid": str(club_instance.id)})
        )
    return form(
        {"userform": club, "showCGU": False, "action_name": _("Edit"),},
        "users/user.html",
        request,
    )


@login_required
@can_edit(User)
def edit_info(request, user, userid):
    """View for editing base user informations.
    Perform an acl check on user instance.

    Parameters:
        request (django request): Standard django request.
        user: User instance to edit

    Returns:
        Django User form.

    """
    if user.is_class_adherent:
        user_form = AdherentEditForm(
            request.POST or None, request.FILES or None, instance=user.adherent, user=request.user
        )
    else:
        user_form = ClubForm(
            request.POST or None, request.FILES or None,instance=user.club, user=request.user
        )
    if user_form.is_valid():
        if user_form.changed_data:
            user = user_form.save(commit=False)
            former_user = Adherent.objects.get(pseudo=user.pseudo)
            if former_user.profile_image:
                if (user.profile_image and user.profile_image.url != former_user.profile_image.url) or (not user.profile_image):
                        former_image = settings.BASE_DIR+former_user.profile_image.url
                        os.remove(former_image)
            user = user_form.save()
            messages.success(request, _("The user was edited."))

            if user.send_confirm_email_if_necessary(request):
                messages.success(request, _("Sent a new confirmation email."))

        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    return form(
        {"userform": user_form, "action_name": _("Edit")}, "users/user.html", request,
    )


@login_required
@can_edit(User, "state")
def state(request, user, userid):
    """View for editing state of user.
    Perform an acl check on user instance, and check if editing user
    has state edition permission.

    Parameters:
        request (django request): Standard django request.
        user: User instance to edit

    Returns:
        Django User form.

    """
    state_form = StateForm(request.POST or None, instance=user)
    if state_form.is_valid():
        if state_form.changed_data:
            user_instance = state_form.save()
            messages.success(request, _("The states were edited."))
            if user_instance.trigger_email_changed_state(request):
                messages.success(
                    request, _("An email to confirm the address was sent.")
                )
        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    return form(
        {"userform": state_form, "action_name": _("Edit")}, "users/user.html", request,
    )


@login_required
@can_edit(User, "groups")
def groups(request, user, userid):
    """View for editing groups of user.
    Perform an acl check on user instance, and check if editing user
    has groups edition permission.

    Parameters:
        request (django request): Standard django request.
        user: User instance to edit

    Returns:
        Django User form.

    """
    group_form = GroupForm(request.POST or None, instance=user, user=request.user)
    if group_form.is_valid():
        if group_form.changed_data:
            group_form.save()
            messages.success(request, _("The groups were edited."))
        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    return form(
        {"userform": group_form, "action_name": _("Edit")}, "users/user.html", request,
    )


@login_required
@can_edit(User, "password")
def password(request, user, userid):
    """View for editing password of user.
    Perform an acl check on user instance, and check if editing user
    has password edition permission.
    If User instance is in critical groups, the edition requires extra
    permission.

    Parameters:
        request (django request): Standard django request.
        user: User instance to edit password

    Returns:
        Django User form.

    """
    u_form = PassForm(request.POST or None, instance=user, user=request.user)
    if u_form.is_valid():
        if u_form.changed_data:
            u_form.save()
            messages.success(request, _("The password was changed."))
        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    return form(
        {"userform": u_form, "action_name": _("Change the password")},
        "users/user.html",
        request,
    )


@login_required
@can_edit(User, "groups")
def del_group(request, user, listrightid, **_kwargs):
    """View for editing groups of user.
    Perform an acl check on user instance, and check if editing user
    has groups edition permission.
    If User instance is in critical groups, the edition requires extra
    permission.

    Parameters:
        request (django request): Standard django request.
        user: User instance to edit groups

    Returns:
        Django User form.

    """
    user.groups.remove(ListRight.objects.get(id=listrightid))
    user.save()
    messages.success(request, _("%s was removed from the group.") % user)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
@can_edit(User, "is_superuser")
def del_superuser(request, user, **_kwargs):
    """View for editing superuser attribute of user.
    Perform an acl check on user instance, and check if editing user
    has edition of superuser flag on target user.

    Parameters:
        request (django request): Standard django request.
        user: User instance to edit superuser flag.

    Returns:
        Django User form.

    """
    user.is_superuser = False
    user.save()
    messages.success(request, _("%s is no longer superuser.") % user)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
@can_create(ServiceUser)
def new_serviceuser(request):
    """View for creation of new serviceuser, for external services on
    ldap tree for auth purpose (dokuwiki, owncloud, etc).
    Perform an acl check on editing user, and check if editing user
    has permission of create new serviceuser.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django ServiceUser form.

    """
    user = ServiceUserForm(request.POST or None)
    if user.is_valid():
        user.save()
        messages.success(request, _("The service user was created."))
        return redirect(reverse("users:index-serviceusers"))
    return form(
        {"userform": user, "action_name": _("Add")}, "users/user.html", request,
    )


@login_required
@can_edit(ServiceUser)
def edit_serviceuser(request, serviceuser, **_kwargs):
    """View for edition of serviceuser, for external services on
    ldap tree for auth purpose (dokuwiki, owncloud, etc).
    Perform an acl check on editing user, and check if editing user
    has permission of edit target serviceuser.

    Parameters:
        request (django request): Standard django request.
        serviceuser: ServiceUser instance to edit attributes.

    Returns:
        Django ServiceUser form.

    """
    serviceuser = EditServiceUserForm(request.POST or None, instance=serviceuser)
    if serviceuser.is_valid():
        if serviceuser.changed_data:
            serviceuser.save()
        messages.success(request, _("The service user was edited."))
        return redirect(reverse("users:index-serviceusers"))
    return form(
        {"userform": serviceuser, "action_name": _("Edit")}, "users/user.html", request,
    )


@login_required
@can_delete(ServiceUser)
def del_serviceuser(request, serviceuser, **_kwargs):
    """View for removing serviceuser, for external services on
    ldap tree for auth purpose (dokuwiki, owncloud, etc).
    Perform an acl check on editing user, and check if editing user
    has permission of deleting target serviceuser.

    Parameters:
        request (django request): Standard django request.
        serviceuser: ServiceUser instance to delete.

    Returns:
        Django ServiceUser form.

    """
    if request.method == "POST":
        serviceuser.delete()
        messages.success(request, _("The service user was deleted."))
        return redirect(reverse("users:index-serviceusers"))
    return form(
        {"objet": serviceuser, "objet_name": _("service user")},
        "users/delete.html",
        request,
    )


@login_required
@can_create(Ban)
@can_edit(User)
def add_ban(request, user, userid):
    """View for adding a ban object for user instance.
    Perform an acl check on editing user, and check if editing user
    has permission of adding a ban on target user, add_ban.
    Syntaxe: DD/MM/AAAA, the ban takes an immediate effect.

    Parameters:
        request (django request): Standard django request.
        user: User instance to add a ban.

    Returns:
        Django Ban form.

    """
    ban_instance = Ban(user=user)
    ban = BanForm(request.POST or None, instance=ban_instance)
    ban.request = request

    if ban.is_valid():
        ban.save()
        messages.success(request, _("The ban was added."))
        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    if user.is_ban():
        messages.error(request, _("Warning: this user already has an active ban."))
    return form({"userform": ban, "action_name": _("Add")}, "users/user.html", request)


@login_required
@can_edit(Ban)
def edit_ban(request, ban_instance, **_kwargs):
    """View for editing a ban object for user instance.
    Perform an acl check on editing user, and check if editing user
    has permission of editing a ban on target user, edit_ban.
    Syntaxe: DD/MM/AAAA, the ban takes an immediate effect.

    Parameters:
        request (django request): Standard django request.
        ban: Ban instance to edit.

    Returns:
        Django Ban form.

    """
    ban = BanForm(request.POST or None, instance=ban_instance)
    ban.request = request

    if ban.is_valid():
        if ban.changed_data:
            ban.save()
            messages.success(request, _("The ban was edited."))
        return redirect(reverse("users:index"))
    return form({"userform": ban, "action_name": _("Edit")}, "users/user.html", request)


@login_required
@can_delete(Ban)
def del_ban(request, ban, **_kwargs):
    """View for removing a ban object for user instance.
    Perform an acl check on editing user, and check if editing user
    has permission of deleting a ban on target user, del_ban.

    Parameters:
        request (django request): Standard django request.
        ban: Ban instance to delete.

    Returns:
        Django Ban form.

    """
    if request.method == "POST":
        ban.delete()
        messages.success(request, _("The ban was deleted."))
        return redirect(reverse("users:profil", kwargs={"userid": str(ban.user.id)}))
    return form({"objet": ban, "objet_name": _("ban")}, "users/delete.html", request)


@login_required
@can_create(Whitelist)
@can_edit(User)
def add_whitelist(request, user, userid):
    """View for adding a whitelist object for user instance.
    Perform an acl check on editing user, and check if editing user
    has permission of adding a wheitelist on target user, add_whitelist.
    Syntaxe: DD/MM/AAAA, the whitelist takes an immediate effect.

    Parameters:
        request (django request): Standard django request.
        user: User instance to add a whitelist.

    Returns:
        Django Whitelist form.

    """
    whitelist_instance = Whitelist(user=user)
    whitelist = WhitelistForm(request.POST or None, instance=whitelist_instance)
    if whitelist.is_valid():
        whitelist.save()
        messages.success(request, _("The whitelist was added."))
        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    if user.is_whitelisted():
        messages.error(
            request, _("Warning: this user already has an active whitelist.")
        )
    return form(
        {"userform": whitelist, "action_name": _("Add")}, "users/user.html", request,
    )


@login_required
@can_edit(Whitelist)
def edit_whitelist(request, whitelist_instance, **_kwargs):
    """View for editing a whitelist object for user instance.
    Perform an acl check on editing user, and check if editing user
    has permission of editing a whitelist on target user, edit_whitelist.
    Syntaxe: DD/MM/AAAA, the whitelist takes an immediate effect.

    Parameters:
        request (django request): Standard django request.
        whitelist: whitelist instance to edit.

    Returns:
        Django Whitelist form.

    """
    whitelist = WhitelistForm(request.POST or None, instance=whitelist_instance)
    if whitelist.is_valid():
        if whitelist.changed_data:
            whitelist.save()
            messages.success(request, _("The whitelist was edited."))
        return redirect(reverse("users:index"))
    return form(
        {"userform": whitelist, "action_name": _("Edit")}, "users/user.html", request,
    )


@login_required
@can_delete(Whitelist)
def del_whitelist(request, whitelist, **_kwargs):
    """View for removing a whitelist object for user instance.
    Perform an acl check on editing user, and check if editing user
    has permission of deleting a whitelist on target user, del_whitelist.

    Parameters:
        request (django request): Standard django request.
        whitelist: Whitelist instance to delete.

    Returns:
        Django Whitelist form.

    """
    if request.method == "POST":
        whitelist.delete()
        messages.success(request, _("The whitelist was deleted."))
        return redirect(
            reverse("users:profil", kwargs={"userid": str(whitelist.user.id)})
        )
    return form(
        {"objet": whitelist, "objet_name": _("whitelist")}, "users/delete.html", request
    )


@login_required
@can_create(EMailAddress)
@can_edit(User)
def add_emailaddress(request, user, userid):
    """View for adding an emailaddress object for user instance.
    Perform an acl check on editing user, and check if editing user
    has permission of adding an emailaddress on target user.

    Parameters:
        request (django request): Standard django request.
        user: User instance to add an emailaddress.

    Returns:
        Django EmailAddress form.

    """
    emailaddress_instance = EMailAddress(user=user)
    emailaddress = EMailAddressForm(
        request.POST or None, instance=emailaddress_instance
    )
    if emailaddress.is_valid():
        emailaddress.save()
        messages.success(request, _("The local email account was created."))
        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    return form(
        {"userform": emailaddress, "showCGU": False, "action_name": _("Add"),},
        "users/user.html",
        request,
    )


@login_required
@can_edit(EMailAddress)
def edit_emailaddress(request, emailaddress_instance, **_kwargs):
    """View for edit an emailaddress object for user instance.
    Perform an acl check on editing user, and check if editing user
    has permission of editing an emailaddress on target user.

    Parameters:
        request (django request): Standard django request.
        emailaddress: Emailaddress to edit.

    Returns:
        Django EmailAddress form.

    """
    emailaddress = EMailAddressForm(
        request.POST or None, instance=emailaddress_instance
    )
    if emailaddress.is_valid():
        if emailaddress.changed_data:
            emailaddress.save()
            messages.success(request, _("The local email account was edited."))
        return redirect(
            reverse(
                "users:profil", kwargs={"userid": str(emailaddress_instance.user.id)}
            )
        )
    return form(
        {"userform": emailaddress, "showCGU": False, "action_name": _("Edit"),},
        "users/user.html",
        request,
    )


@login_required
@can_delete(EMailAddress)
def del_emailaddress(request, emailaddress, **_kwargs):
    """View for deleting an emailaddress object for user instance.
    Perform an acl check on editing user, and check if editing user
    has permission of deleting an emailaddress on target user.

    Parameters:
        request (django request): Standard django request.
        emailaddress: Emailaddress to delete.

    Returns:
        Django EmailAddress form.

    """
    if request.method == "POST":
        emailaddress.delete()
        messages.success(request, _("The local email account was deleted."))
        return redirect(
            reverse("users:profil", kwargs={"userid": str(emailaddress.user.id)})
        )
    return form(
        {"objet": emailaddress, "objet_name": _("email address")},
        "users/delete.html",
        request,
    )


@login_required
@can_edit(User)
def edit_email_settings(request, user_instance, **_kwargs):
    """View for editing User's emailaddress settings for user instance.
    Perform an acl check on editing user, and check if editing user
    has permission of editing email settings on target user.

    Parameters:
        request (django request): Standard django request.
        user: User instance to edit email settings.

    Returns:
        Django User form.

    """
    email_settings = EmailSettingsForm(
        request.POST or None, instance=user_instance, user=request.user
    )
    if email_settings.is_valid():
        if email_settings.changed_data:
            email_settings.save()
            messages.success(request, _("The email settings were edited."))

            if user_instance.send_confirm_email_if_necessary(request):
                messages.success(
                    request, _("An email to confirm your address was sent.")
                )

        return redirect(
            reverse("users:profil", kwargs={"userid": str(user_instance.id)})
        )
    return form(
        {
            "userform": email_settings,
            "showCGU": False,
            "load_js_file": "/static/js/email_address.js",
            "action_name": _("Edit"),
        },
        "users/user.html",
        request,
    )


@login_required
@can_create(School)
def add_school(request):
    """View for adding a new school object.
    Perform an acl check on editing user, and check if editing user
    has permission of adding a new school, add_school.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django School form.

    """
    school = SchoolForm(request.POST or None)
    if school.is_valid():
        school.save()
        messages.success(request, _("The school was added."))
        return redirect(reverse("users:index-school"))
    return form(
        {"userform": school, "action_name": _("Add")}, "users/user.html", request,
    )


@login_required
@can_edit(School)
def edit_school(request, school_instance, **_kwargs):
    """View for editing a school instance object.
    Perform an acl check on editing user, and check if editing user
    has permission of editing a school, edit_school.

    Parameters:
        request (django request): Standard django request.
        school_instance: school instance to edit.

    Returns:
        Django School form.

    """
    school = SchoolForm(request.POST or None, instance=school_instance)
    if school.is_valid():
        if school.changed_data:
            school.save()
            messages.success(request, _("The school was edited."))
        return redirect(reverse("users:index-school"))
    return form(
        {"userform": school, "action_name": _("Edit")}, "users/user.html", request,
    )


@login_required
@can_delete_set(School)
def del_school(request, instances):
    """View for deleting a school instance object.
    Perform an acl check on editing user, and check if editing user
    has permission of deleting a school, del_school.
    A school can be deleted only if it is not assigned to a user (mode
    protect).

    Parameters:
        request (django request): Standard django request.
        school_instance: school instance to delete.

    Returns:
        Django School form.

    """
    school = DelSchoolForm(request.POST or None, instances=instances)
    if school.is_valid():
        school_dels = school.cleaned_data["schools"]
        for school_del in school_dels:
            try:
                school_del.delete()
                messages.success(request, _("The school was deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    _(
                        "The school %s is assigned to at least one user,"
                        " impossible to delete it."
                    )
                    % school_del,
                )
        return redirect(reverse("users:index-school"))
    return form(
        {"userform": school, "action_name": _("Confirm")}, "users/user.html", request
    )


@login_required
@can_create(ListShell)
def add_shell(request):
    """View for adding a new linux shell object.
    Perform an acl check on editing user, and check if editing user
    has permission of adding a new shell, add_school.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django Shell form.

    """
    shell = ShellForm(request.POST or None)
    if shell.is_valid():
        shell.save()
        messages.success(request, _("The shell was added."))
        return redirect(reverse("users:index-shell"))
    return form(
        {"userform": shell, "action_name": _("Add")}, "users/user.html", request
    )


@login_required
@can_edit(ListShell)
def edit_shell(request, shell_instance, **_kwargs):
    """View for editing a shell instance object.
    Perform an acl check on editing user, and check if editing user
    has permission of editing a shell, edit_shell.

    Parameters:
        request (django request): Standard django request.
        shell_instance: shell instance to edit.

    Returns:
        Django Shell form.

    """
    shell = ShellForm(request.POST or None, instance=shell_instance)
    if shell.is_valid():
        if shell.changed_data:
            shell.save()
            messages.success(request, _("The shell was edited."))
        return redirect(reverse("users:index-shell"))
    return form(
        {"userform": shell, "action_name": _("Edit")}, "users/user.html", request,
    )


@login_required
@can_delete(ListShell)
def del_shell(request, shell, **_kwargs):
    """View for deleting a shell instance object.
    Perform an acl check on editing user, and check if editing user
    has permission of deleting a shell, del_shell.
    A shell can be deleted only if it is not assigned to a user (mode
    protect).

    Parameters:
        request (django request): Standard django request.
        shell_instance: shell instance to delete.

    Returns:
        Django Shell form.

    """
    if request.method == "POST":
        shell.delete()
        messages.success(request, _("The shell was deleted."))
        return redirect(reverse("users:index-shell"))
    return form(
        {"objet": shell, "objet_name": _("shell")}, "users/delete.html", request
    )


@login_required
@can_create(ListRight)
def add_listright(request):
    """View for adding a new group of rights and users (listright linked to groups)
    object for user instance.
    Perform an acl check on editing user, and check if editing user
    has permission of adding a new listright.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django ListRight form.

    """
    listright = NewListRightForm(request.POST or None)
    if listright.is_valid():
        listright.save()
        messages.success(request, _("The group of rights was added."))
        return redirect(reverse("users:index-listright"))
    return form(
        {"form": listright, "action_name": _("Add"), "permissions": permission_tree()},
        "users/edit_listright.html",
        request,
    )


@login_required
@can_edit(ListRight)
def edit_listright(request, listright_instance, **_kwargs):
    """View for editing a listright instance object.
    Perform an acl check on editing user, and check if editing user
    has permission of editing a listright, edit_listright.

    Parameters:
        request (django request): Standard django request.
        listright_instance: listright instance to edit.

    Returns:
        Django ListRight form.

    """
    listright_form = ListRightForm(request.POST or None, instance=listright_instance)
    if listright_form.is_valid():
        if listright_form.changed_data:
            listright_form.save()
            messages.success(request, _("The group of rights was edited."))
        return redirect(reverse("users:index-listright"))
    return form(
        {
            "form": listright_form,
            "action_name": _("Edit"),
            "permissions": permission_tree(),
            "instance": listright_instance,
        },
        "users/edit_listright.html",
        request,
    )


@login_required
@can_delete_set(ListRight)
def del_listright(request, instances):
    """View for deleting a listright instance object.
    Perform an acl check on editing user, and check if editing user
    has permission of deleting a listright, del_listright.
    A listright/group can be deleted only if it is empty (mode
    protect).

    Parameters:
        request (django request): Standard django request.
        listright_instance: listright instance to delete.

    Returns:
        Django ListRight form.

    """
    listright = DelListRightForm(request.POST or None, instances=instances)
    if listright.is_valid():
        listright_dels = listright.cleaned_data["listrights"]
        for listright_del in listright_dels:
            try:
                listright_del.delete()
                messages.success(request, _("The group of rights was deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    _(
                        "The group of rights %s is assigned to at least one"
                        " user, impossible to delete it."
                    )
                    % listright_del,
                )
        return redirect(reverse("users:index-listright"))
    return form(
        {"userform": listright, "action_name": _("Confirm")}, "users/user.html", request
    )


@login_required
@can_view_all(User)
@can_change(User, "state")
def mass_archive(request):
    """View for performing a mass archive operation.
    Check if editing User has the acl for globaly changing "State"
    flag on users, and can edit all the users.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django User form.

    """
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    to_archive_form = MassArchiveForm(request.POST or None)
    to_archive_list = []
    if to_archive_form.is_valid():
        date = to_archive_form.cleaned_data["date"]
        full_archive = to_archive_form.cleaned_data["full_archive"]
        to_archive_list = (
            User.objects.exclude(id__in=all_has_access())
            .exclude(id__in=all_has_access(search_time=date))
            .exclude(state=User.STATE_NOT_YET_ACTIVE)
            .exclude(state=User.STATE_FULL_ARCHIVE)
        )
        if not full_archive:
            to_archive_list = to_archive_list.exclude(state=User.STATE_ARCHIVE)
        if "valider" in request.POST:
            if full_archive:
                User.mass_full_archive(to_archive_list)
            else:
                User.mass_archive(to_archive_list)
            messages.success(
                request, _("%s users were archived.") % to_archive_list.count()
            )
            return redirect(reverse("users:index"))
        to_archive_list = re2o_paginator(request, to_archive_list, pagination_number)
    return form(
        {"userform": to_archive_form, "to_archive_list": to_archive_list},
        "users/mass_archive.html",
        request,
    )


@login_required
@can_view_all(Adherent)
def index(request):
    """View for displaying the paginated list of all users/adherents in re2o.
    Need the global acl for viewing all users, can_view_all.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django Adherent Form.

    """
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    users_list = Adherent.objects.select_related("room")
    users_list = SortTable.sort(
        users_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.USERS_INDEX,
    )
    users_list = re2o_paginator(request, users_list, pagination_number)
    return render(request, "users/index.html", {"users_list": users_list})


@login_required
@can_view_all(Club)
def index_clubs(request):
    """View for displaying the paginated list of all users/clubs in re2o.
    Need the global acl for viewing all users, can_view_all.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django Adherent Form.

    """
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    clubs_list = Club.objects.select_related("room")
    clubs_list = SortTable.sort(
        clubs_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.USERS_INDEX,
    )
    clubs_list = re2o_paginator(request, clubs_list, pagination_number)
    return render(request, "users/index_clubs.html", {"clubs_list": clubs_list})


@login_required
@can_view_all(Ban)
def index_ban(request):
    """View for displaying the paginated list of all bans in re2o.
    Need the global acl for viewing all bans, can_view_all.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django Ban Form.

    """
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    ban_list = Ban.objects.select_related("user")
    ban_list = SortTable.sort(
        ban_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.USERS_INDEX_BAN,
    )
    ban_list = re2o_paginator(request, ban_list, pagination_number)
    return render(request, "users/index_ban.html", {"ban_list": ban_list})


@login_required
@can_view_all(Whitelist)
def index_white(request):
    """View for displaying the paginated list of all whitelists in re2o.
    Need the global acl for viewing all whitelists, can_view_all.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django Whitelist Form.

    """
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    white_list = Whitelist.objects.select_related("user")
    white_list = SortTable.sort(
        white_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.USERS_INDEX_BAN,
    )
    white_list = re2o_paginator(request, white_list, pagination_number)
    return render(request, "users/index_whitelist.html", {"white_list": white_list})


@login_required
@can_view_all(School)
def index_school(request):
    """View for displaying the paginated list of all schools in re2o.
    Need the global acl for viewing all schools, can_view_all.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django School Form.

    """
    school_list = School.objects.order_by("name")
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    school_list = SortTable.sort(
        school_list,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.USERS_INDEX_SCHOOL,
    )
    school_list = re2o_paginator(request, school_list, pagination_number)
    return render(request, "users/index_schools.html", {"school_list": school_list})


@login_required
@can_view_all(ListShell)
def index_shell(request):
    """View for displaying the paginated list of all shells in re2o.
    Need the global acl for viewing all shells, can_view_all.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django Shell Form.

    """
    shell_list = ListShell.objects.order_by("shell")
    return render(request, "users/index_shell.html", {"shell_list": shell_list})


@login_required
@can_view_all(ListRight)
def index_listright(request):
    """View for displaying the listrights/groups list in re2o.
    The listrights are sorted by members users, and individual
    acl for a complete display.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django ListRight Form.

    """
    rights = {}
    for right in (
        ListRight.objects.order_by("name")
        .prefetch_related("permissions")
        .prefetch_related("user_set")
    ):
        rights[right] = right.user_set.annotate(
            action_number=Count("revision"), last_seen=Max("revision__date_created")
        )
    superusers = User.objects.filter(is_superuser=True).annotate(
        action_number=Count("revision"), last_seen=Max("revision__date_created")
    )
    return render(
        request,
        "users/index_listright.html",
        {"rights": rights, "superusers": superusers},
    )


@login_required
@can_view_all(ServiceUser)
def index_serviceusers(request):
    """View for displaying the paginated list of all serviceusers in re2o
    See ServiceUser model for more informations on service users.
    Need the global acl for viewing all serviceusers, can_view_all.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django ServiceUser Form.

    """
    serviceusers_list = ServiceUser.objects.order_by("pseudo")
    return render(
        request,
        "users/index_serviceusers.html",
        {"serviceusers_list": serviceusers_list},
    )


@login_required
def mon_profil(request):
    """Shortcuts view to profil view, with correct arguments.
    Returns the view profil with users argument, users is set to
    default request.user. 

    Parameters:
        request (django request): Standard django request.

    Returns:
        Django User Profil Form.

    """
    return redirect(reverse("users:profil", kwargs={"userid": str(request.user.id)}))


@login_required
@can_view(User)
def profil(request, users, **_kwargs):
    """Profil view. Display informations on users, the single user.
    Informations displayed are:
        * Adherent or Club User instance informations
        * Interface/Machine belonging to User instance
        * Invoice belonging to User instance
        * Ban instances belonging to User
        * Whitelists instances belonging to User
        * Email Settings of User instance
        * Tickets belonging to User instance.
    Requires the acl can_view on user instance.
 
    Parameters:
        request (django request): Standard django request.
        users: User instance to display profil

    Returns:
        Django User Profil Form.
    """

    # Generate the template list for all apps of re2o if relevant
    apps = [import_module(app) for app in LOCAL_APPS + OPTIONNAL_APPS_RE2O]
    apps_templates_list = [
        app.views.aff_profil(request, users)
        for app in apps
        if hasattr(app.views, "aff_profil")
    ]

    nb_machines = users.user_interfaces().count()
    
    bans = Ban.objects.filter(user=users)
    bans = SortTable.sort(
        bans,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.USERS_INDEX_BAN,
    )
    whitelists = Whitelist.objects.filter(user=users)
    whitelists = SortTable.sort(
        whitelists,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.USERS_INDEX_WHITE,
    )
    try:
        balance = find_payment_method(Paiement.objects.get(is_balance=True))
    except Paiement.DoesNotExist:
        user_solde = False
    else:
        user_solde = balance is not None and balance.can_credit_balance(request.user)
    return render(
        request,
        "users/profil.html",
        {
            "users": users,
            "nb_machines":nb_machines,
            "apps_templates_list": apps_templates_list,
            "ban_list": bans,
            "white_list": whitelists,
            "user_solde": user_solde,
            "solde_activated": Paiement.objects.filter(is_balance=True).exists(),
            "asso_name": AssoOption.objects.first().name,
            "emailaddress_list": users.email_address,
            "local_email_accounts_enabled": (
                OptionalUser.objects.first().local_email_accounts_enabled
            ),
        },
    )


def reset_password(request):
    """Reset password form, linked to form forgotten password.
    If an user is found, send an email to him with a link
    to reset its password.
    
    Parameters:
        request (django request): Standard django request.

    Returns:
        Django ResetPassword Form.

    """
    userform = ResetPasswordForm(request.POST or None)
    if userform.is_valid():
        try:
            user = User.objects.get(
                pseudo=userform.cleaned_data["pseudo"],
                email=userform.cleaned_data["email"],
                state__in=[User.STATE_ACTIVE, User.STATE_NOT_YET_ACTIVE],
            )
        except User.DoesNotExist:
            messages.error(request, _("The user doesn't exist."))
            return form(
                {"userform": userform, "action_name": _("Reset")},
                "users/user.html",
                request,
            )
        user.reset_passwd_mail(request)
        messages.success(request, _("An email to reset the password was sent."))
        redirect(reverse("index"))
    return form(
        {"userform": userform, "action_name": _("Reset")}, "users/user.html", request
    )


def process(request, token):
    """Process view, in case of both reset password, or confirm email in case
    of new email set.
    This view calls process_passwd or process_email.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Correct Django process Form.

    """
    valid_reqs = Request.objects.filter(expires_at__gt=timezone.now())
    req = get_object_or_404(valid_reqs, token=token)

    if req.type == Request.PASSWD:
        return process_passwd(request, req)
    elif req.type == Request.EMAIL:
        return process_email(request, req)
    else:
        messages.error(request, _("Error: please contact an admin."))
        redirect(reverse("index"))


def process_passwd(request, req):
    """Process view, in case of reset password by email. Returns
    a form to change and reset the password.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Correct Django process password Form.

    """
    user = req.user
    u_form = PassForm(request.POST or None, instance=user, user=request.user)
    if u_form.is_valid():
        with transaction.atomic(), reversion.create_revision():
            user.confirm_mail()
            u_form.save()
            reversion.set_comment("Password reset")

        # Delete all remaining requests
        Request.objects.filter(user=user, type=Request.PASSWD).delete()
        messages.success(request, _("The password was changed."))
        return redirect(reverse("index"))
    return form(
        {"userform": u_form, "action_name": _("Change the password")},
        "users/user.html",
        request,
    )


def process_email(request, req):
    """Process view, in case of confirm a new email. Returns
    a form to notify the success of the email confirmation to
    request.User.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Correct Django process email Form.

    """
    user = req.user
    if request.method == "POST":
        with transaction.atomic(), reversion.create_revision():
            user.confirm_mail()
            user.save()
            reversion.set_comment("Email confirmation")

        # Delete all remaining requests
        Request.objects.filter(user=user, type=Request.EMAIL).delete()
        messages.success(request, _("The %s address was confirmed." % user.email))
        return redirect(reverse("index"))

    return form(
        {"email": user.email, "name": user.get_full_name()},
        "users/confirm_email.html",
        request,
    )


@login_required
@can_edit(User)
def resend_confirmation_email(request, logged_user, userid):
    """View to resend confirm email, for adding a new email.
    Check if User has the correct acl.

    Parameters:
        request (django request): Standard django request.

    Returns:
        Correct Django resend email Form.

    """
    try:
        user = User.objects.get(
            id=userid,
            email_state__in=[User.EMAIL_STATE_PENDING, User.EMAIL_STATE_UNVERIFIED],
        )
    except User.DoesNotExist:
        messages.error(request, _("The user doesn't exist."))

    if request.method == "POST":
        user.confirm_email_address_mail(request)
        messages.success(request, _("An email to confirm your address was sent."))
        return redirect(reverse("users:profil", kwargs={"userid": userid}))

    return form({"email": user.email}, "users/resend_confirmation_email.html", request)


@login_required
def initial_register(request):
    """View to register both a new room, and a new interface/machine for a user.
    This view is used with switchs function of redirect web after AAA authentication
    failed. Then, the users log-in, and the new mac-address and switch port, in order to
    get the room, are included in HTTP Headers by the switch redirection functionnality.
    This allow to add the new interface with the correct mac-address, and confirm if needed,
    the new room of request.user.

    Parameters:
        request (django request): Standard django request.

    Returns:
         Initial room and interface/machine register Form.

    """
    switch_ip = request.GET.get("switch_ip", None)
    switch_port = request.GET.get("switch_port", None)
    client_mac = request.GET.get("client_mac", None)
    u_form = InitialRegisterForm(
        request.POST or None,
        user=request.user,
        switch_ip=switch_ip,
        switch_port=switch_port,
        client_mac=client_mac,
    )
    if not u_form.fields:
        messages.error(request, _("Incorrect URL, or already registered device."))
        return redirect(
            reverse("users:profil", kwargs={"userid": str(request.user.id)})
        )
    if switch_ip and switch_port:
        port = Port.objects.filter(
            switch__interface__ipv4__ipv4=switch_ip, port=switch_port
        ).first()
    if u_form.is_valid():
        messages.success(
            request,
            _(
                "Successful registration! Please"
                " disconnect and reconnect your Ethernet"
                " cable to get Internet access."
            ),
        )
        return form({}, "users/plugin_out.html", request)
    return form(
        {"userform": u_form, "port": port, "mac": client_mac},
        "users/user_autocapture.html",
        request,
    )

