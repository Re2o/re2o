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
from django.db.models import Sum

from preferences.models import GeneralOption
from re2o.acl import (
    can_create,
    can_delete,
    can_delete_set,
    can_edit,
    can_view_all,
)
from re2o.base import re2o_paginator
from re2o.views import form
from users.models import User
from cotisations.models import Paiement

from .forms import DepositForm, DepositItemForm, DelDepositItemForm
from .models import Deposit, DepositItem
from .utils import DepositSortTable


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
@can_view_all(Deposit, DepositItem, Paiement, User)
def index_deposits(request):
    """
    View used to display the list of all deposits.
    """
    pagination_number = GeneralOption.get_cached_value("pagination_number")

    # Get the list of all deposits, sorted according to the user's request
    deposits_list = Deposit.objects.select_related("user", "item", "payment_method")
    deposits_list = DepositSortTable.sort(
        deposits_list,
        request.GET.get("col"),
        request.GET.get("order"),
        DepositSortTable.DEPOSIT_INDEX,
    )
    nbr_deposits = deposits_list.count()

    # Split it into 2: the list of those which have not yet been returned...
    lent_deposits_list = deposits_list.filter(returned=False)
    nbr_deposits_lent = lent_deposits_list.count()
    lent_deposits_list = re2o_paginator(
        request, lent_deposits_list, pagination_number, page_arg="lpage"
    )

    # ... and the list of those that have already been returned
    returned_deposits_list = deposits_list.filter(returned=True)
    returned_deposits_list = re2o_paginator(
        request, returned_deposits_list, pagination_number, page_arg="rpage"
    )

    return render(
        request,
        "deposits/index_deposits.html",
        {
            "lent_deposits_list": lent_deposits_list,
            "returned_deposits_list": returned_deposits_list,
            "nbr_deposits": nbr_deposits,
            "nbr_deposits_lent": nbr_deposits_lent,
        },
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
        item_del = item.cleaned_data["deposit_items"]
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


@login_required
@can_view_all(Deposit, DepositItem, Paiement, User)
def index_stats(request):
    """
    View used to display general statistics about deposits
    """
    # We want to build a list of tables for statistics
    stats = []

    # Statistics for payment methods
    payment_data = []
    for method in Paiement.objects.order_by("moyen"):
        deposits = Deposit.objects.filter(payment_method=method)
        amount = deposits.aggregate(Sum("deposit_amount")).get(
            "deposit_amount__sum", None
        )
        payment_data.append(
            (
                method.moyen,
                deposits.filter(returned=False).count(),
                deposits.filter(returned=True).count(),
                deposits.count(),
                "{} €".format(amount or 0),
            )
        )

    stats.append(
        {
            "title": _("Deposits by payment method"),
            "headers": [
                _("Payment method"),
                _("Unreturned deposits"),
                _("Returned deposits"),
                _("Total"),
                _("Amount"),
            ],
            "data": payment_data,
        }
    )

    # Statistics for deposit items
    items_data = []
    for item in DepositItem.objects.order_by("name"):
        deposits = Deposit.objects.filter(item=item)
        amount = deposits.aggregate(Sum("deposit_amount")).get(
            "deposit_amount__sum", None
        )
        items_data.append(
            (
                item.name,
                deposits.filter(returned=False).count(),
                deposits.filter(returned=True).count(),
                deposits.count(),
                "{} €".format(amount or 0),
            )
        )

    stats.append(
        {
            "title": _("Deposits by item type"),
            "headers": [
                _("Deposit item"),
                _("Unreturned deposits"),
                _("Returned deposits"),
                _("Total"),
                _("Amount"),
            ],
            "data": items_data,
        }
    )

    # Statistics for amounts
    pending_amount = (
        Deposit.objects.filter(returned=False)
        .aggregate(Sum("deposit_amount"))
        .get("deposit_amount__sum", None)
    )
    returned_amount = (
        Deposit.objects.filter(returned=True)
        .aggregate(Sum("deposit_amount"))
        .get("deposit_amount__sum", None)
    )

    amounts_data = [
        (
            _("Not yet returned"),
            Deposit.objects.filter(returned=False).count(),
            "{} €".format(pending_amount or 0),
        ),
        (
            _("Already returned"),
            Deposit.objects.filter(returned=True).count(),
            "{} €".format(returned_amount or 0),
        ),
    ]

    stats.append(
        {
            "title": _("Deposits amounts"),
            "headers": [
                _("Category"),
                _("Total"),
                _("Amount"),
            ],
            "data": amounts_data,
        }
    )

    return render(request, "deposits/index_stats.html", {"stats_list": stats})


# Canonic views for optional apps
def aff_profil(request, user):
    """View used to display the deposits on a user's profile."""
    deposits_list = Deposit.objects.filter(user=user).select_related(
        "user", "item", "payment_method"
    )
    deposits_list = DepositSortTable.sort(
        deposits_list,
        request.GET.get("col"),
        request.GET.get("order"),
        DepositSortTable.DEPOSIT_INDEX,
    )
    pagination_number = GeneralOption.get_cached_value("pagination_large_number")

    deposits = re2o_paginator(request, deposits_list, pagination_number)
    context = {
        "users": user,
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
