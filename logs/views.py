# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Gabriel Détraz
# Copyright © 2018  Lara Kermarec
# Copyright © 2018  Augustin Lemesle
# Copyright © 2018  Hugo Levy-Falk
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

# App de gestion des statistiques pour re2o
# Gabriel Détraz
# Gplv2
"""
Vues des logs et statistiques générales.

La vue index générale affiche une selection des dernières actions,
classées selon l'importance, avec date, et user formatés.

Stats_logs renvoie l'ensemble des logs.

Les autres vues sont thématiques, ensemble des statistiques et du
nombre d'objets par models, nombre d'actions par user, etc
"""

from __future__ import unicode_literals

from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db.models import Count
from django.apps import apps
from django.utils.translation import ugettext as _

from reversion.models import Revision
from reversion.models import Version, ContentType

from users.models import (
    User,
    ServiceUser,
    School,
    ListRight,
    ListShell,
    Ban,
    Whitelist,
    Adherent,
    Club,
)
from cotisations.models import Facture, Vente, Article, Banque, Paiement, Cotisation
from machines.models import (
    Machine,
    MachineType,
    IpType,
    Extension,
    Interface,
    Domain,
    IpList,
    OuverturePortList,
    Service,
    Vlan,
    Nas,
    SOA,
    Mx,
    Ns,
)
from topologie.models import (
    Switch,
    Port,
    Room,
    Stack,
    ModelSwitch,
    ConstructorSwitch,
    AccessPoint,
)
from preferences.models import GeneralOption
from re2o.views import form
from re2o.utils import (
    all_whitelisted,
    all_baned,
    all_has_access,
    all_adherent,
    all_active_assigned_interfaces_count,
    all_active_interfaces_count,
)
from re2o.base import re2o_paginator, SortTable
from re2o.acl import can_view_all, can_view_app, can_edit_history, can_view

from .models import (
    ActionsSearch,
    RevisionAction,
    MachineHistorySearch,
    get_history_class,
)

from .forms import ActionsSearchForm, MachineHistorySearchForm


@login_required
@can_view_app("logs")
def index(request):
    """View used to display summary of events about users."""
    pagination_number = GeneralOption.get_cached_value("pagination_number")
    # The types of content kept for display
    content_type_filter = ["ban", "whitelist", "vente", "interface", "user"]
    # Select only wanted versions
    versions = Version.objects.filter(
        content_type__in=ContentType.objects.filter(model__in=content_type_filter)
    ).select_related("revision")
    versions = SortTable.sort(
        versions, request.GET.get("col"), request.GET.get("order"), SortTable.LOGS_INDEX
    )
    versions = re2o_paginator(request, versions, pagination_number)
    # Force to have a list instead of QuerySet
    versions.count(0)
    # Items to remove later because invalid
    to_remove = []
    # Parse every item (max = pagination_number)
    for i in range(len(versions.object_list)):
        if versions.object_list[i].object:
            version = versions.object_list[i]
            versions.object_list[i] = {
                "rev_id": version.revision.id,
                "comment": version.revision.comment,
                "datetime": version.revision.date_created,
                "username": version.revision.user.get_username()
                if version.revision.user
                else "?",
                "user_id": version.revision.user_id,
                "version": version,
            }
        else:
            to_remove.insert(0, i)
    # Remove all tagged invalid items
    for i in to_remove:
        versions.object_list.pop(i)
    return render(request, "logs/index.html", {"versions_list": versions})


@login_required
@can_view_all(GeneralOption)
def stats_logs(request):
    """View used to do an advanced search through the logs."""
    actions_form = ActionsSearchForm(request.GET or None)

    if actions_form.is_valid():
        actions = ActionsSearch()
        revisions = actions.get(actions_form.cleaned_data)
        revisions = SortTable.sort(
            revisions,
            request.GET.get("col"),
            request.GET.get("order"),
            SortTable.LOGS_STATS_LOGS,
        )

        pagination_number = GeneralOption.get_cached_value("pagination_number")
        revisions = re2o_paginator(request, revisions, pagination_number)

        # Only do this now so it's not applied to objects which aren't displayed
        # It can take a bit of time because it has to compute the diff of each version
        revisions.object_list = [RevisionAction(r) for r in revisions.object_list]
        return render(request, "logs/stats_logs.html", {"revisions_list": revisions})

    return render(
        request, "logs/search_stats_logs.html", {"actions_form": actions_form}
    )


@login_required
@can_edit_history
def revert_action(request, revision_id):
    """View used to revert actions."""
    try:
        revision = Revision.objects.get(id=revision_id)
    except Revision.DoesNotExist:
        messages.error(request, _("Nonexistent revision."))
    if request.method == "POST":
        revision.revert()
        messages.success(request, _("The action was deleted."))
        return redirect(reverse("logs:index"))
    return form(
        {"objet": revision, "objet_name": revision.__class__.__name__},
        "logs/delete.html",
        request,
    )


@login_required
@can_view_all(IpList, Interface, User)
def stats_general(request):
    """View used to display general statistics about users (activated,
    disabled, archived etc.) and IP addresses (ranges, number of assigned
    addresses etc.).
    """
    ip_dict = dict()
    for ip_range in IpType.objects.select_related("vlan").all():
        all_ip = IpList.objects.filter(ip_type=ip_range)
        used_ip = Interface.objects.filter(ipv4__in=all_ip).count()
        active_ip = (
            all_active_assigned_interfaces_count()
            .filter(ipv4__in=IpList.objects.filter(ip_type=ip_range))
            .count()
        )
        ip_dict[ip_range] = [
            ip_range,
            ip_range.vlan,
            all_ip.count(),
            used_ip,
            active_ip,
            all_ip.count() - used_ip,
        ]
    _all_adherent = all_adherent(including_asso=False)
    _all_has_access = all_has_access(including_asso=False)
    _all_baned = all_baned()
    _all_whitelisted = all_whitelisted()
    _all_active_interfaces_count = all_active_interfaces_count()
    _all_active_assigned_interfaces_count = all_active_assigned_interfaces_count()
    stats = [
        [  # First set of data (about users)
            [  # Headers
                _("Category"),
                _("Number of users (members and clubs)"),
                _("Number of members"),
                _("Number of clubs"),
            ],
            {  # Data
                "active_users": [
                    _("Activated users"),
                    User.objects.filter(state=User.STATE_ACTIVE).count(),
                    (Adherent.objects.filter(state=Adherent.STATE_ACTIVE).count()),
                    Club.objects.filter(state=Club.STATE_ACTIVE).count(),
                ],
                "inactive_users": [
                    _("Disabled users"),
                    User.objects.filter(state=User.STATE_DISABLED).count(),
                    (Adherent.objects.filter(state=Adherent.STATE_DISABLED).count()),
                    Club.objects.filter(state=Club.STATE_DISABLED).count(),
                ],
                "archive_users": [
                    _("Archived users"),
                    User.objects.filter(state=User.STATE_ARCHIVE).count(),
                    (Adherent.objects.filter(state=Adherent.STATE_ARCHIVE).count()),
                    Club.objects.filter(state=Club.STATE_ARCHIVE).count(),
                ],
                "full_archive_users": [
                    _("Fully archived users"),
                    User.objects.filter(state=User.STATE_FULL_ARCHIVE).count(),
                    (
                        Adherent.objects.filter(
                            state=Adherent.STATE_FULL_ARCHIVE
                        ).count()
                    ),
                    Club.objects.filter(state=Club.STATE_FULL_ARCHIVE).count(),
                ],
                "not_active_users": [
                    _("Not yet active users"),
                    User.objects.filter(state=User.STATE_NOT_YET_ACTIVE).count(),
                    (
                        Adherent.objects.filter(
                            state=Adherent.STATE_NOT_YET_ACTIVE
                        ).count()
                    ),
                    Club.objects.filter(state=Club.STATE_NOT_YET_ACTIVE).count(),
                ],
                "adherent_users": [
                    _("Contributing members"),
                    _all_adherent.count(),
                    _all_adherent.exclude(adherent__isnull=True).count(),
                    _all_adherent.exclude(club__isnull=True).count(),
                ],
                "connexion_users": [
                    _("Users benefiting from a connection"),
                    _all_has_access.count(),
                    _all_has_access.exclude(adherent__isnull=True).count(),
                    _all_has_access.exclude(club__isnull=True).count(),
                ],
                "ban_users": [
                    _("Banned users"),
                    _all_baned.count(),
                    _all_baned.exclude(adherent__isnull=True).count(),
                    _all_baned.exclude(club__isnull=True).count(),
                ],
                "whitelisted_user": [
                    _("Users benefiting from a free connection"),
                    _all_whitelisted.count(),
                    _all_whitelisted.exclude(adherent__isnull=True).count(),
                    _all_whitelisted.exclude(club__isnull=True).count(),
                ],
                "email_state_verified_users": [
                    _("Users with a confirmed email"),
                    User.objects.filter(email_state=User.EMAIL_STATE_VERIFIED).count(),
                    Adherent.objects.filter(
                        email_state=User.EMAIL_STATE_VERIFIED
                    ).count(),
                    Club.objects.filter(email_state=User.EMAIL_STATE_VERIFIED).count(),
                ],
                "email_state_unverified_users": [
                    _("Users with an unconfirmed email"),
                    User.objects.filter(
                        email_state=User.EMAIL_STATE_UNVERIFIED
                    ).count(),
                    Adherent.objects.filter(
                        email_state=User.EMAIL_STATE_UNVERIFIED
                    ).count(),
                    Club.objects.filter(
                        email_state=User.EMAIL_STATE_UNVERIFIED
                    ).count(),
                ],
                "email_state_pending_users": [
                    _("Users pending email confirmation"),
                    User.objects.filter(email_state=User.EMAIL_STATE_PENDING).count(),
                    Adherent.objects.filter(
                        email_state=User.EMAIL_STATE_PENDING
                    ).count(),
                    Club.objects.filter(email_state=User.EMAIL_STATE_PENDING).count(),
                ],
                "actives_interfaces": [
                    _("Active interfaces (with access to the network)"),
                    _all_active_interfaces_count.count(),
                    (
                        _all_active_interfaces_count.exclude(
                            machine__user__adherent__isnull=True
                        ).count()
                    ),
                    (
                        _all_active_interfaces_count.exclude(
                            machine__user__club__isnull=True
                        ).count()
                    ),
                ],
                "actives_assigned_interfaces": [
                    _("Active interfaces assigned IPv4"),
                    _all_active_assigned_interfaces_count.count(),
                    (
                        _all_active_assigned_interfaces_count.exclude(
                            machine__user__adherent__isnull=True
                        ).count()
                    ),
                    (
                        _all_active_assigned_interfaces_count.exclude(
                            machine__user__club__isnull=True
                        ).count()
                    ),
                ],
            },
        ],
        [  # Second set of data (about ip adresses)
            [  # Headers
                _("IP range"),
                _("VLAN"),
                _("Total number of IP addresses"),
                _("Number of assigned IP addresses"),
                _("Number of IP address assigned to an activated machine"),
                _("Number of unassigned IP addresses"),
            ],
            ip_dict,  # Data already prepared
        ],
    ]
    return render(request, "logs/stats_general.html", {"stats_list": stats})


@login_required
@can_view_app("users", "cotisations", "machines", "topologie")
def stats_models(request):
    """View used to display general statistics about the number of objects
    stored in the database, for each model.
    """
    stats = {
        _("Users (members and clubs)"): {
            "users": [User._meta.verbose_name, User.objects.count()],
            "adherents": [Adherent._meta.verbose_name, Adherent.objects.count()],
            "clubs": [Club._meta.verbose_name, Club.objects.count()],
            "serviceuser": [
                ServiceUser._meta.verbose_name,
                ServiceUser.objects.count(),
            ],
            "school": [School._meta.verbose_name, School.objects.count()],
            "listright": [ListRight._meta.verbose_name, ListRight.objects.count()],
            "listshell": [ListShell._meta.verbose_name, ListShell.objects.count()],
            "ban": [Ban._meta.verbose_name, Ban.objects.count()],
            "whitelist": [Whitelist._meta.verbose_name, Whitelist.objects.count()],
        },
        Cotisation._meta.verbose_name_plural.title(): {
            "factures": [Facture._meta.verbose_name, Facture.objects.count()],
            "vente": [Vente._meta.verbose_name, Vente.objects.count()],
            "cotisation": [Cotisation._meta.verbose_name, Cotisation.objects.count()],
            "article": [Article._meta.verbose_name, Article.objects.count()],
            "banque": [Banque._meta.verbose_name, Banque.objects.count()],
        },
        Machine._meta.verbose_name_plural.title(): {
            "machine": [Machine._meta.verbose_name, Machine.objects.count()],
            "typemachine": [
                MachineType._meta.verbose_name,
                MachineType.objects.count(),
            ],
            "typeip": [IpType._meta.verbose_name, IpType.objects.count()],
            "extension": [Extension._meta.verbose_name, Extension.objects.count()],
            "interface": [Interface._meta.verbose_name, Interface.objects.count()],
            "alias": [
                Domain._meta.verbose_name,
                Domain.objects.exclude(cname=None).count(),
            ],
            "iplist": [IpList._meta.verbose_name, IpList.objects.count()],
            "service": [Service._meta.verbose_name, Service.objects.count()],
            "ouvertureportlist": [
                OuverturePortList._meta.verbose_name,
                OuverturePortList.objects.count(),
            ],
            "vlan": [Vlan._meta.verbose_name, Vlan.objects.count()],
            "SOA": [SOA._meta.verbose_name, SOA.objects.count()],
            "Mx": [Mx._meta.verbose_name, Mx.objects.count()],
            "Ns": [Ns._meta.verbose_name, Ns.objects.count()],
            "nas": [Nas._meta.verbose_name, Nas.objects.count()],
        },
        _("Topology"): {
            "switch": [Switch._meta.verbose_name, Switch.objects.count()],
            "bornes": [AccessPoint._meta.verbose_name, AccessPoint.objects.count()],
            "port": [Port._meta.verbose_name, Port.objects.count()],
            "chambre": [Room._meta.verbose_name, Room.objects.count()],
            "stack": [Stack._meta.verbose_name, Stack.objects.count()],
            "modelswitch": [
                ModelSwitch._meta.verbose_name,
                ModelSwitch.objects.count(),
            ],
            "constructorswitch": [
                ConstructorSwitch._meta.verbose_name,
                ConstructorSwitch.objects.count(),
            ],
        },
        _("Actions performed"): {
            "revision": [_("Number of actions"), Revision.objects.count()]
        },
    }
    return render(request, "logs/stats_models.html", {"stats_list": stats})


@login_required
@can_view_app("users")
def stats_users(request):
    """View used to display statistics aggregated by user (number of machines,
    bans, whitelists, rights etc.).
    """
    stats = {
        User._meta.verbose_name: {
            Machine._meta.verbose_name_plural: User.objects.annotate(
                num=Count("machine")
            ).order_by("-num")[:10],
            Facture._meta.verbose_name_plural: User.objects.annotate(
                num=Count("facture")
            ).order_by("-num")[:10],
            Ban._meta.verbose_name_plural: User.objects.annotate(
                num=Count("ban")
            ).order_by("-num")[:10],
            Whitelist._meta.verbose_name_plural: User.objects.annotate(
                num=Count("whitelist")
            ).order_by("-num")[:10],
            _("rights"): User.objects.annotate(num=Count("groups")).order_by("-num")[
                :10
            ],
        },
        School._meta.verbose_name: {
            User._meta.verbose_name_plural: School.objects.annotate(
                num=Count("user")
            ).order_by("-num")[:10]
        },
        Paiement._meta.verbose_name: {
            User._meta.verbose_name_plural: Paiement.objects.annotate(
                num=Count("facture")
            ).order_by("-num")[:10]
        },
        Banque._meta.verbose_name: {
            User._meta.verbose_name_plural: Banque.objects.annotate(
                num=Count("facture")
            ).order_by("-num")[:10]
        },
    }
    return render(request, "logs/stats_users.html", {"stats_list": stats})


@login_required
@can_view_app("users")
def stats_actions(request):
    """View used to display the number of actions, aggregated by user."""
    stats = {
        User._meta.verbose_name: {
            _("actions"): User.objects.annotate(num=Count("revision")).order_by("-num")[
                :40
            ]
        }
    }
    return render(request, "logs/stats_users.html", {"stats_list": stats})


@login_required
@can_view_app("users")
def stats_search_machine_history(request):
    """View used to display the history of machines with the given IP or MAC
    address.
    """
    history_form = MachineHistorySearchForm(request.GET or None)
    if history_form.is_valid():
        history = MachineHistorySearch()
        events = history.get(
            history_form.cleaned_data.get("q", ""), history_form.cleaned_data
        )
        max_result = GeneralOption.get_cached_value("pagination_number")
        events = re2o_paginator(request, events, max_result)

        return render(request, "logs/machine_history.html", {"events": events},)
    return render(
        request, "logs/search_machine_history.html", {"history_form": history_form}
    )


def get_history_object(request, model, object_name, object_id):
    """Get the objet of type model with the given object_id
    Handles permissions and DoesNotExist errors
    """
    try:
        instance = model.get_instance(object_id)
    except model.DoesNotExist:
        instance = None

    if instance is None:
        authorized = can_view_app("logs")
        msg = None
    else:
        authorized, msg, _permissions = instance.can_view(request.user)

    if not authorized:
        messages.error(
            request, msg or _("You don't have the right to access this menu.")
        )
        return (
            False,
            redirect(reverse("users:profil", kwargs={"userid": str(request.user.id)})),
        )

    return True, instance


@login_required
def history(request, application, object_name, object_id):
    """Render history for a model.

    The model is determined using the `HISTORY_BIND` dictionnary if none is
    found, raises a Http404. The view checks if the user is allowed to see the
    history using the `can_view` method of the model, or the generic
    `can_view_app("logs")` for deleted objects (see `get_history_object`).

    Args:
        request: The request sent by the user.
        application: Name of the application.
        object_name: Name of the model.
        object_id: Id of the object you want to acces history.

    Returns:
        The rendered page of history if access is granted, else the user is
        redirected to their profile page, with an error message.

    Raises:
        Http404: This kind of models doesn't have history.
    """
    try:
        model = apps.get_model(application, object_name)
    except LookupError:
        raise Http404(_("No model found."))

    authorized, instance = get_history_object(request, model, object_name, object_id)
    if not can_view:
        return instance

    history = get_history_class(model)
    events = history.get(int(object_id), model)

    # Events is None if object wasn't found
    if events is None:
        messages.error(request, _("Nonexistent entry."))
        return redirect(
            reverse("users:profil", kwargs={"userid": str(request.user.id)})
        )

    # Generate the pagination with the objects
    max_result = GeneralOption.get_cached_value("pagination_number")
    events = re2o_paginator(request, events, max_result)

    # Add a default title in case the object was deleted
    title = instance or "{} ({})".format(history.name, _("Deleted"))

    return render(
        request,
        "re2o/history.html",
        {"title": title, "events": events, "related_history": history.related},
    )
