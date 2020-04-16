# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
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

# App de gestion des users pour re2o
# Lara Kermarec, Gabriel Détraz, Lemesle Augustin
# Gplv2
"""
Module des views.

On définit les vues pour l'ajout, l'edition des users : infos personnelles,
mot de passe, etc

Permet aussi l'ajout, edition et suppression des droits, des bannissements,
des whitelist, des services users et des écoles
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
from re2o.settings_local import OPTIONNAL_APPS_RE2O
from re2o.views import form
from re2o.utils import all_has_access
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
from .serializers import MailingSerializer, MailingMemberSerializer
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
    ConfirmMailForm,
    ResetPasswordForm,
    ClubAdminandMembersForm,
    GroupForm,
    InitialRegisterForm,
)


@can_create(Adherent)
def new_user(request):
    """ Vue de création d'un nouvel utilisateur,
    envoie un mail pour le mot de passe"""
    user = AdherentCreationForm(request.POST or None, user=request.user)
    GTU_sum_up = GeneralOption.get_cached_value("GTU_sum_up")
    GTU = GeneralOption.get_cached_value("GTU")
    is_set_password_allowed = OptionalUser.get_cached_value("allow_set_password_during_user_creation")

    if user.is_valid():
        user = user.save()

        # Use "is False" so that if None, the email is sent
        if is_set_password_allowed and user.should_send_password_reset_email is False:
            user.confirm_email_address_mail(request)
            messages.success(
                request,
                _("The user %s was created.")
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
    """ Vue de création d'un nouveau club,
    envoie un mail pour le mot de passe"""
    club = ClubForm(request.POST or None, user=request.user)
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
    """Vue d'edition de la liste des users administrateurs et
    membres d'un club"""
    club = ClubAdminandMembersForm(request.POST or None, instance=club_instance)
    if club.is_valid():
        if club.changed_data:
            club.save()
            messages.success(request, _("The club was edited."))
        return redirect(
            reverse("users:profil", kwargs={"userid": str(club_instance.id)})
        )
    return form(
        {
            "userform": club,
            "showCGU": False,
            "action_name": _("Edit"),
        },
        "users/user.html",
        request,
    )


@login_required
@can_edit(User)
def edit_info(request, user, userid):
    """ Edite un utilisateur à partir de son id,
    si l'id est différent de request.user, vérifie la
    possession du droit cableur """
    if user.is_class_adherent:
        user_form = AdherentEditForm(
            request.POST or None, instance=user.adherent, user=request.user
        )
    else:
        user_form = ClubForm(
            request.POST or None, instance=user.club, user=request.user
        )
    if user_form.is_valid():
        if user_form.changed_data:
            user_form.save()
            messages.success(request, _("The user was edited."))
        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    return form(
        {"userform": user_form, "action_name": _("Edit")},
        "users/user.html",
        request,
    )


@login_required
@can_edit(User, "state")
def state(request, user, userid):
    """ Change the state (active/unactive/archived) of a user"""
    state_form = StateForm(request.POST or None, instance=user)
    if state_form.is_valid():
        if state_form.changed_data:
            state_form.save()
            messages.success(request, _("The state was edited."))
        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    return form(
        {"userform": state_form, "action_name": _("Edit")},
        "users/user.html",
        request,
    )


@login_required
@can_edit(User, "groups")
def groups(request, user, userid):
    """ View to edit the groups of a user """
    group_form = GroupForm(request.POST or None, instance=user, user=request.user)
    if group_form.is_valid():
        if group_form.changed_data:
            group_form.save()
            messages.success(request, _("The groups were edited."))
        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    return form(
        {"userform": group_form, "action_name": _("Edit")},
        "users/user.html",
        request,
    )


@login_required
@can_edit(User, "password")
def password(request, user, userid):
    """ Reinitialisation d'un mot de passe à partir de l'userid,
    pour self par défaut, pour tous sans droit si droit cableur,
    pour tous si droit bureau """
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
    """ View used to delete a group """
    user.groups.remove(ListRight.objects.get(id=listrightid))
    user.save()
    messages.success(request, _("%s was removed from the group.") % user)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
@can_edit(User, "is_superuser")
def del_superuser(request, user, **_kwargs):
    """Remove the superuser right of an user."""
    user.is_superuser = False
    user.save()
    messages.success(request, _("%s is no longer superuser.") % user)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
@can_create(ServiceUser)
def new_serviceuser(request):
    """ Vue de création d'un nouvel utilisateur service"""
    user = ServiceUserForm(request.POST or None)
    if user.is_valid():
        user.save()
        messages.success(request, _("The service user was created."))
        return redirect(reverse("users:index-serviceusers"))
    return form(
        {"userform": user, "action_name": _("Add")},
        "users/user.html",
        request,
    )


@login_required
@can_edit(ServiceUser)
def edit_serviceuser(request, serviceuser, **_kwargs):
    """ Edit a ServiceUser """
    serviceuser = EditServiceUserForm(request.POST or None, instance=serviceuser)
    if serviceuser.is_valid():
        if serviceuser.changed_data:
            serviceuser.save()
        messages.success(request, _("The service user was edited."))
        return redirect(reverse("users:index-serviceusers"))
    return form(
        {"userform": serviceuser, "action_name": _("Edit")},
        "users/user.html",
        request,
    )


@login_required
@can_delete(ServiceUser)
def del_serviceuser(request, serviceuser, **_kwargs):
    """Suppression d'un ou plusieurs serviceusers"""
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
    """ Ajouter un banissement, nécessite au moins le droit bofh
    (a fortiori bureau)
    Syntaxe : JJ/MM/AAAA , heure optionnelle, prend effet immédiatement"""
    ban_instance = Ban(user=user)
    ban = BanForm(request.POST or None, instance=ban_instance)
    if ban.is_valid():
        ban.save()
        messages.success(request, _("The ban was added."))
        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    if user.is_ban():
        messages.error(request, _("Warning: this user already has an active ban."))
    return form(
        {"userform": ban, "action_name": _("Add")}, "users/user.html", request
    )


@login_required
@can_edit(Ban)
def edit_ban(request, ban_instance, **_kwargs):
    """ Editer un bannissement, nécessite au moins le droit bofh
    (a fortiori bureau)
    Syntaxe : JJ/MM/AAAA , heure optionnelle, prend effet immédiatement"""
    ban = BanForm(request.POST or None, instance=ban_instance)
    if ban.is_valid():
        if ban.changed_data:
            ban.save()
            messages.success(request, _("The ban was edited."))
        return redirect(reverse("users:index"))
    return form(
        {"userform": ban, "action_name": _("Edit")}, "users/user.html", request
    )


@login_required
@can_delete(Ban)
def del_ban(request, ban, **_kwargs):
    """ Supprime un banissement"""
    if request.method == "POST":
        ban.delete()
        messages.success(request, _("The ban was deleted."))
        return redirect(reverse("users:profil", kwargs={"userid": str(ban.user.id)}))
    return form({"objet": ban, "objet_name": _("ban")}, "users/delete.html", request)


@login_required
@can_create(Whitelist)
@can_edit(User)
def add_whitelist(request, user, userid):
    """ Accorder un accès gracieux, temporaire ou permanent.
    Need droit cableur
    Syntaxe : JJ/MM/AAAA , heure optionnelle, prend effet immédiatement,
    raison obligatoire"""
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
        {"userform": whitelist, "action_name": _("Add")},
        "users/user.html",
        request,
    )


@login_required
@can_edit(Whitelist)
def edit_whitelist(request, whitelist_instance, **_kwargs):
    """ Editer un accès gracieux, temporaire ou permanent.
    Need droit cableur
    Syntaxe : JJ/MM/AAAA , heure optionnelle, prend effet immédiatement,
    raison obligatoire"""
    whitelist = WhitelistForm(request.POST or None, instance=whitelist_instance)
    if whitelist.is_valid():
        if whitelist.changed_data:
            whitelist.save()
            messages.success(request, _("The whitelist was edited."))
        return redirect(reverse("users:index"))
    return form(
        {"userform": whitelist, "action_name": _("Edit")},
        "users/user.html",
        request,
    )


@login_required
@can_delete(Whitelist)
def del_whitelist(request, whitelist, **_kwargs):
    """ Supprime un acces gracieux"""
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
    """ Create a new local email account"""
    emailaddress_instance = EMailAddress(user=user)
    emailaddress = EMailAddressForm(
        request.POST or None, instance=emailaddress_instance
    )
    if emailaddress.is_valid():
        emailaddress.save()
        messages.success(request, _("The local email account was created."))
        return redirect(reverse("users:profil", kwargs={"userid": str(userid)}))
    return form(
        {
            "userform": emailaddress,
            "showCGU": False,
            "action_name": _("Add"),
        },
        "users/user.html",
        request,
    )


@login_required
@can_edit(EMailAddress)
def edit_emailaddress(request, emailaddress_instance, **_kwargs):
    """ Edit a local email account"""
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
        {
            "userform": emailaddress,
            "showCGU": False,
            "action_name": _("Edit"),
        },
        "users/user.html",
        request,
    )


@login_required
@can_delete(EMailAddress)
def del_emailaddress(request, emailaddress, **_kwargs):
    """Delete a local email account"""
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
    """Edit the email settings of a user"""
    email_settings = EmailSettingsForm(
        request.POST or None, instance=user_instance, user=request.user
    )
    if email_settings.is_valid():
        if email_settings.changed_data:
            email_settings.save()
            messages.success(request, _("The email settings were edited."))
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
    """ Ajouter un établissement d'enseignement à la base de donnée,
    need cableur"""
    school = SchoolForm(request.POST or None)
    if school.is_valid():
        school.save()
        messages.success(request, _("The school was added."))
        return redirect(reverse("users:index-school"))
    return form(
        {"userform": school, "action_name": _("Add")},
        "users/user.html",
        request,
    )


@login_required
@can_edit(School)
def edit_school(request, school_instance, **_kwargs):
    """ Editer un établissement d'enseignement à partir du schoolid dans
    la base de donnée, need cableur"""
    school = SchoolForm(request.POST or None, instance=school_instance)
    if school.is_valid():
        if school.changed_data:
            school.save()
            messages.success(request, _("The school was edited."))
        return redirect(reverse("users:index-school"))
    return form(
        {"userform": school, "action_name": _("Edit")},
        "users/user.html",
        request,
    )


@login_required
@can_delete_set(School)
def del_school(request, instances):
    """ Supprimer un établissement d'enseignement à la base de donnée,
    need cableur
    Objet protégé, possible seulement si aucun user n'est affecté à
    l'établissement """
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
    """ Ajouter un shell à la base de donnée"""
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
    """ Editer un shell à partir du listshellid"""
    shell = ShellForm(request.POST or None, instance=shell_instance)
    if shell.is_valid():
        if shell.changed_data:
            shell.save()
            messages.success(request, _("The shell was edited."))
        return redirect(reverse("users:index-shell"))
    return form(
        {"userform": shell, "action_name": _("Edit")},
        "users/user.html",
        request,
    )


@login_required
@can_delete(ListShell)
def del_shell(request, shell, **_kwargs):
    """Destruction d'un shell"""
    if request.method == "POST":
        shell.delete()
        messages.success(request, _("The shell was deleted."))
        return redirect(reverse("users:index-shell"))
    return form({"objet": shell, "objet_name": _("shell")}, "users/delete.html", request)


@login_required
@can_create(ListRight)
def add_listright(request):
    """ Ajouter un droit/groupe, nécessite droit bureau.
    Obligation de fournir un gid pour la synchro ldap, unique """
    listright = NewListRightForm(request.POST or None)
    if listright.is_valid():
        listright.save()
        messages.success(request, _("The group of rights was added."))
        return redirect(reverse("users:index-listright"))
    return form(
        {"userform": listright, "action_name": _("Add")},
        "users/user.html",
        request,
    )


@login_required
@can_edit(ListRight)
def edit_listright(request, listright_instance, **_kwargs):
    """ Editer un groupe/droit, necessite droit bureau,
    à partir du listright id """
    listright = ListRightForm(request.POST or None, instance=listright_instance)
    if listright.is_valid():
        if listright.changed_data:
            listright.save()
            messages.success(request, _("The group of rights was edited."))
        return redirect(reverse("users:index-listright"))
    return form(
        {"userform": listright, "action_name": _("Edit")},
        "users/user.html",
        request,
    )


@login_required
@can_delete_set(ListRight)
def del_listright(request, instances):
    """ Supprimer un ou plusieurs groupe, possible si il est vide, need droit
    bureau """
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
    """ Permet l'archivage massif"""
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
            .exclude(state=User.STATE_EMAIL_NOT_YET_CONFIRMED)
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
    """ Affiche l'ensemble des adherents, need droit cableur """
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
    """ Affiche l'ensemble des clubs, need droit cableur """
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
    """ Affiche l'ensemble des ban, need droit cableur """
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
    """ Affiche l'ensemble des whitelist, need droit cableur """
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
    """ Affiche l'ensemble des établissement"""
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
    """ Affiche l'ensemble des shells"""
    shell_list = ListShell.objects.order_by("shell")
    return render(request, "users/index_shell.html", {"shell_list": shell_list})


@login_required
@can_view_all(ListRight)
def index_listright(request):
    """ Affiche l'ensemble des droits"""
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
    """ Affiche les users de services (pour les accès ldap)"""
    serviceusers_list = ServiceUser.objects.order_by("pseudo")
    return render(
        request,
        "users/index_serviceusers.html",
        {"serviceusers_list": serviceusers_list},
    )


@login_required
def mon_profil(request):
    """ Lien vers profil, renvoie request.id à la fonction """
    return redirect(reverse("users:profil", kwargs={"userid": str(request.user.id)}))


@login_required
@can_view(User)
def profil(request, users, **_kwargs):
    """ Affiche un profil, self or cableur, prend un userid en argument """
    machines = (
        Machine.objects.filter(user=users)
        .select_related("user")
        .prefetch_related("interface_set__domain__extension")
        .prefetch_related("interface_set__ipv4__ip_type__extension")
        .prefetch_related("interface_set__machine_type")
        .prefetch_related("interface_set__domain__related_domain__extension")
    )
    machines = SortTable.sort(
        machines,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.MACHINES_INDEX,
    )

    optionnal_apps = [import_module(app) for app in OPTIONNAL_APPS_RE2O]
    optionnal_templates_list = [
        app.views.profil(request, users)
        for app in optionnal_apps
        if hasattr(app.views, "profil")
    ]

    pagination_large_number = GeneralOption.get_cached_value("pagination_large_number")
    nb_machines = machines.count()
    machines = re2o_paginator(request, machines, pagination_large_number)
    factures = Facture.objects.filter(user=users)
    factures = SortTable.sort(
        factures,
        request.GET.get("col"),
        request.GET.get("order"),
        SortTable.COTISATIONS_INDEX,
    )
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
            "machines_list": machines,
            "nb_machines": nb_machines,
            "optionnal_templates_list": optionnal_templates_list,
            "facture_list": factures,
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
    """ Reintialisation du mot de passe si mdp oublié """
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
    """Process, lien pour la reinitialisation du mot de passe"""
    valid_reqs = Request.objects.filter(expires_at__gt=timezone.now())
    req = get_object_or_404(valid_reqs, token=token)

    if req.type == Request.PASSWD:
        return process_passwd(request, req)
    else:
        messages.error(request, _("Error: please contact an admin."))
        redirect(reverse("index"))


def process_passwd(request, req):
    """Process le changeemnt de mot de passe, renvoie le formulaire
    demandant le nouveau password"""
    user = req.user
    u_form = PassForm(request.POST or None, instance=user, user=request.user)
    if u_form.is_valid():
        with transaction.atomic(), reversion.create_revision():
            u_form.save()
            reversion.set_comment("Password reset")
        req.delete()
        messages.success(request, _("The password was changed."))
        return redirect(reverse("index"))
    return form(
        {"userform": u_form, "action_name": _("Change the password")},
        "users/user.html",
        request,
    )


def confirm_email(request, token):
    """Lien pour la confirmation de l'email"""
    valid_reqs = Request.objects.filter(expires_at__gt=timezone.now())
    req = get_object_or_404(valid_reqs, token=token)

    if req.type == Request.EMAIL:
        return process_email(request, req)
    else:
        messages.error(request, _("Error: please contact an admin."))
        redirect(reverse("index"))


def process_email(request, req):
    """Process la confirmation de mail, renvoie le formulaire
    de validation"""
    user = req.user
    u_form = ConfirmMailForm(request.POST or None, instance=user, user=request.user)
    if u_form.is_valid():
        with transaction.atomic(), reversion.create_revision():
            u_form.save()
            reversion.set_comment("Email confirmation")
        req.delete()
        messages.success(request, _("The email was confirmed."))
        return redirect(reverse("index"))

    return form(
        {"userform": u_form, "action_name": _("Confirm the email")},
        "users/user.html",
        request,
    )


@login_required
def initial_register(request):
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


class JSONResponse(HttpResponse):
    """ Framework Rest """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs["content_type"] = "application/json"
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
@login_required
@permission_required("machines.serveur")
def ml_std_list(_request):
    """ API view sending all the available standard mailings"""
    return JSONResponse([{"name": "adherents"}])


@csrf_exempt
@login_required
@permission_required("machines.serveur")
def ml_std_members(request, ml_name):
    """ API view sending all the members for a standard mailing"""
    # All with active connextion
    if ml_name == "adherents":
        members = all_has_access().values("email").distinct()
    # Unknown mailing
    else:
        messages.error(request, _("The mailing list doesn't exist."))
        return redirect(reverse("index"))
    seria = MailingMemberSerializer(members, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required("machines.serveur")
def ml_club_list(_request):
    """ API view sending all the available club mailings"""
    clubs = Club.objects.filter(mailing=True).values("pseudo")
    seria = MailingSerializer(clubs, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required("machines.serveur")
def ml_club_admins(request, ml_name):
    """ API view sending all the administrators for a specific club mailing"""
    try:
        club = Club.objects.get(mailing=True, pseudo=ml_name)
    except Club.DoesNotExist:
        messages.error(request, _("The mailing list doesn't exist."))
        return redirect(reverse("index"))
    members = club.administrators.all().values("email").distinct()
    seria = MailingMemberSerializer(members, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required("machines.serveur")
def ml_club_members(request, ml_name):
    """ API view sending all the members for a specific club mailing"""
    try:
        club = Club.objects.get(mailing=True, pseudo=ml_name)
    except Club.DoesNotExist:
        messages.error(request, _("The mailing list doesn't exist."))
        return redirect(reverse("index"))
    members = (
        club.administrators.all().values("email").distinct()
        | club.members.all().values("email").distinct()
    )
    seria = MailingMemberSerializer(members, many=True)
    return JSONResponse(seria.data)
