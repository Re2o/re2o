# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2021  Jean-Romain Garnier
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
Deposits views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext as _

from preferences.models import GeneralOption
from re2o.acl import (
    can_create,
    can_delete,
    can_delete_set,
    can_edit,
    can_view,
    can_view_all,
)
from re2o.base import re2o_paginator
from re2o.views import form
from users.models import User

from .forms import DepositForm, DepositItemForm, DelDepositItemForm
from .models import Deposit, DepositItem


@login_required
@can_create(Deposit)
@can_edit(User)
def new_deposit(request, user, userid):
    """
    View called to create a new deposit.
    """
    deposit = Deposit(user=user)
    # Building the invoice form and the article formset
    deposit_form = DepositForm(
        request.POST or None, instance=deposit, user=request.user, creation=True
    )

    if deposit_form.is_valid():
        deposit_form.save()
        messages.success(request, _("The deposit was created."))
        return redirect(reverse("users:profil", kwargs={"userid": deposit.user.pk}))

    return form(
        {
            "depositform": deposit_form,
            "action_name": _("Confirm"),
            "title": _("New deposit"),
        },
        "deposits/deposit.html",
        request,
    )


@login_required
@can_edit(Deposit)
def edit_deposit(request, deposit, **_kwargs):
    """
    View used to edit an existing deposit.
    """
    deposit_form = DepositForm(
        request.POST or None, instance=deposit, user=request.user
    )
    if deposit_form.is_valid():
        deposit_form.save()
        messages.success(request, _("The deposit was edited."))
        return redirect(reverse("users:profil", kwargs={"userid": deposit.user.pk}))

    return form(
        {
            "depositform": deposit_form,
            "action_name": _("Edit"),
            "title": _("Edit deposit"),
        },
        "deposits/deposit.html",
        request,
    )


@login_required
@can_delete(Deposit)
def del_deposit(request, deposit, **_kwargs):
    """
    View used to delete an existing deposit.
    """
    if request.method == "POST":
        deposit.delete()
        messages.success(request, _("The deposit was deleted."))
        return redirect(reverse("users:profil", kwargs={"userid": deposit.user.pk}))
    return form(
        {"object": deposit, "objet_name": _("deposit")},
        "deposits/delete.html",
        request,
    )


@login_required
@can_view(Deposit)
def aff_deposit(request, deposit, **_kwargs):
    """
    View used to view an existing deposit.
    """
    return render(
        request,
        "deposits/aff_deposit.html",
        {"deposit": deposit},
    )


@login_required
@can_edit(Deposit)
def change_deposit_status(request, deposit, depositid):
    """View used to change a ticket's status."""
    deposit.returned = not deposit.solved
    deposit.save()
    return redirect(
        reverse("deposits:aff-deposit", kwargs={"depositid": str(depositid)})
    )


@login_required
@can_create(DepositItem)
def add_deposit_item(request):
    """
    View used to add a deposit item.
    """
    item = DepositItemForm(request.POST or None)
    if item.is_valid():
        item.save()
        messages.success(request, _("The item was created."))
        return redirect(reverse("deposits:index-deposit-item"))
    return form(
        {
            "depositform": item,
            "action_name": _("Add"),
            "title": _("New deposit item"),
        },
        "deposits/deposit.html",
        request,
    )


@login_required
@can_edit(DepositItem)
def edit_deposit_item(request, item_instance, **_kwargs):
    """
    View used to edit a deposit item.
    """
    item = DepositItemForm(request.POST or None, instance=item_instance)
    if item.is_valid():
        if item.changed_data:
            item.save()
            messages.success(request, _("The item was edited."))
        return redirect(reverse("deposits:index-deposit-item"))
    return form(
        {
            "depositform": item,
            "action_name": _("Edit"),
            "title": _("Edit deposit item"),
        },
        "deposits/deposit.html",
        request,
    )


@login_required
@can_delete_set(DepositItem)
def del_deposit_item(request, instances):
    """
    View used to delete one of the deposit items.
    """
    item = DelDepositItemForm(request.POST or None, instances=instances)
    if item.is_valid():
        item_del = item.cleaned_data["items"]
        item_del.delete()
        messages.success(request, _("The items were deleted."))
        return redirect(reverse("deposits:index-deposit-item"))
    return form(
        {
            "depositform": item,
            "action_name": _("Delete"),
            "title": _("Delete deposit item"),
        },
        "deposits/deposit.html",
        request,
    )


@login_required
@can_view_all(DepositItem)
def index_deposit_item(request):
    """
    View used to display the list of all available deposit items.
    """
    # TODO : Offer other means of sorting
    item_list = DepositItem.objects.order_by("name")
    return render(request, "deposits/index_deposit_item.html", {"item_list": item_list})


# Canonic views for optional apps
def aff_profil(request, user):
    """View used to display the deposits on a user's profile."""
    deposits_list = Deposit.objects.filter(user=user).all().order_by("-date")
    pagination_number = GeneralOption.get_cached_value("pagination_large_number")

    deposits = re2o_paginator(request, deposits_list, pagination_number)
    context = {
        "deposits_list": deposits,
    }
    return render_to_string(
        "deposits/aff_profil.html", context=context, request=request, using=None
    )


def navbar_user():
    """View used to display a link to deposit items in the navbar (in the dropdown
    menu Treasury).
    """
    return ("cotisations", render_to_string("deposits/navbar.html"))
