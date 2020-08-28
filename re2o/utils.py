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

# -*- coding: utf-8 -*-
# David Sinquin, Gabriel Détraz, Lara Kermarec
"""
A group of very usefull functions for re2o core

Functions:
    - find all active users
    - find all active interfaces
    - find all bans
    etc
"""


from __future__ import unicode_literals

from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import Permission, Group

from cotisations.models import Cotisation, Facture, Vente
from machines.models import Interface, Machine
from users.models import Adherent, User, Ban, Whitelist
from preferences.models import AssoOption


def get_group_having_permission(*permission_name):
    """Return all django groups having this permission

    Parameters:
        permission name (string): Permission name

    Returns:
        re2o groups: Groups having this permission

    """
    groups = set()
    for name in permission_name:
        if "." in name:
            app_label, codename = name.split(".")
            permission = Permission.objects.get(
                content_type__app_label=app_label, codename=codename
            )
            groups = groups.union(permission.group_set.all())
        else:
            groups = groups.union(
                Group.objects.filter(
                    permissions__in=Permission.objects.filter(
                        content_type__app_label="users"
                    )
                ).distinct()
            )
    return groups


def all_adherent(search_time=None, including_asso=True):
    """Return all people who have a valid membership at org. Optimised to make only one
    sql query. Build a filter and then apply it to User. Check for each user if a valid
    membership is registered at the desired search_time.
    
    Parameters:
        search_time (django datetime): Datetime to perform this search,
        if not provided, search_time will be set à timezone.now()
        including_asso (boolean): Decide if org itself is included in results

    Returns:
        django queryset: Django queryset containing all users with valid membership 

    """
    if search_time is None:
        search_time = timezone.now()
    filter_user = Q(
        facture__in=Facture.objects.filter(
            vente__in=Vente.objects.filter(
                Q(type_cotisation="All") | Q(type_cotisation="Adhesion"),
                cotisation__in=Cotisation.objects.filter(
                    vente__in=Vente.objects.filter(
                        facture__in=Facture.objects.all().exclude(valid=False)
                    )
                ).filter(Q(date_start__lt=search_time) & Q(date_end__gt=search_time)),
            )
        )
    )
    if including_asso:
        asso_user = AssoOption.get_cached_value("utilisateur_asso")
        if asso_user:
            filter_user |= Q(id=asso_user.id)
    return User.objects.filter(filter_user).distinct()


def all_baned(search_time=None):
    """Return all people who are banned at org. Optimised to make only one
    sql query. Build a filter and then apply it to User. Check for each user 
    banned at the desired search_time.
    
    Parameters:
        search_time (django datetime): Datetime to perform this search,
        if not provided, search_time will be set à timezone.now()

    Returns:
        django queryset: Django queryset containing all users banned  

    """
    if search_time is None:
        search_time = timezone.now()
    return User.objects.filter(
        ban__in=Ban.objects.filter(
            Q(date_start__lt=search_time) & Q(date_end__gt=search_time)
        )
    ).distinct()


def all_whitelisted(search_time=None):
    """Return all people who have a free access at org. Optimised to make only one
    sql query. Build a filter and then apply it to User. Check for each user with a
    whitelisted free access at the desired search_time.
    
    Parameters:
        search_time (django datetime): Datetime to perform this search,
        if not provided, search_time will be set à timezone.now()

    Returns:
        django queryset: Django queryset containing all users whitelisted  

    """
    if search_time is None:
        search_time = timezone.now()
    return User.objects.filter(
        whitelist__in=Whitelist.objects.filter(
            Q(date_start__lt=search_time) & Q(date_end__gt=search_time)
        )
    ).distinct()


def all_has_access(search_time=None, including_asso=True):
    """Return all people who have an valid internet access at org. Optimised to make 
    only one sql query. Build a filter and then apply it to User. Return users 
    with a whitelist, or a valid paid access, except banned users.

    Parameters:
        search_time (django datetime): Datetime to perform this search,
        if not provided, search_time will be set à timezone.now()
        including_asso (boolean): Decide if org itself is included in results

    Returns:
        django queryset: Django queryset containing all valid connection users  

    """
    if search_time is None:
        search_time = timezone.now()
    filter_user = (
        Q(state=User.STATE_ACTIVE)
        & ~Q(email_state=User.EMAIL_STATE_UNVERIFIED)
        & ~Q(
            ban__in=Ban.objects.filter(
                Q(date_start__lt=search_time) & Q(date_end__gt=search_time)
            )
        )
        & (
            Q(
                whitelist__in=Whitelist.objects.filter(
                    Q(date_start__lt=search_time) & Q(date_end__gt=search_time)
                )
            )
            | Q(
                facture__in=Facture.objects.filter(
                    vente__in=Vente.objects.filter(
                        cotisation__in=Cotisation.objects.filter(
                            Q(type_cotisation="All") | Q(type_cotisation="Connexion"),
                            vente__in=Vente.objects.filter(
                                facture__in=Facture.objects.all().exclude(valid=False)
                            ),
                        ).filter(
                            Q(date_start__lt=search_time) & Q(date_end__gt=search_time)
                        )
                    )
                )
            )
        )
    )
    if including_asso:
        asso_user = AssoOption.get_cached_value("utilisateur_asso")
        if asso_user:
            filter_user |= Q(id=asso_user.id)
    return User.objects.filter(filter_user).distinct()


def filter_active_interfaces(interface_set):
    """Return a filter for filtering all interfaces of people who have an valid
    internet access at org.
    Call all_active_interfaces and then apply filter of theses active users on an
    interfaces_set

    Parameters:
        interface_set (django queryset): A queryset of interfaces to perform filter

    Returns:
        django filter: Django filter to apply to an interfaces queryset, 
        will return when applied all active interfaces, related with
        a user with valid membership

    """
    return (
        interface_set.filter(
            machine__in=Machine.objects.filter(user__in=all_has_access()).filter(
                active=True
            )
        )
        .select_related("domain")
        .select_related("machine")
        .select_related("machine_type")
        .select_related("ipv4")
        .select_related("domain__extension")
        .select_related("ipv4__ip_type")
        .distinct()
    )


def filter_complete_interfaces(interface_set):
    """Return a filter for filtering all interfaces of people who have an valid
    internet access at org.
    Call all_active_interfaces and then apply filter of theses active users on an
    interfaces_set. Less efficient than filter_active_interfaces, with a prefetch_related
    on ipv6

    Parameters:
        interface_set (django queryset): A queryset of interfaces to perform filter

    Returns:
        django filter: Django filter to apply to an interfaces queryset, 
        will return when applied all active interfaces, related with
        a user with valid membership

    """
    return filter_active_interfaces(interface_set).prefetch_related("ipv6list")


def all_active_interfaces(full=False):
    """Return a filter for filtering all interfaces of people who have an valid
    internet access at org.
    Call filter_active_interfaces or filter_complete_interfaces.

    Parameters:
        full (boolean): A queryset of interfaces to perform filter. If true, will perform
        a complete filter with filter_complete_interfaces

    Returns:
        django queryset: Django queryset containing all active interfaces, related with
        a user with valid membership

    """
    if full:
        return filter_complete_interfaces(Interface.objects)
    else:
        return filter_active_interfaces(Interface.objects)


def all_active_assigned_interfaces(full=False):
    """Return all interfaces of people who have an valid internet access at org,
    and with valid ipv4.
    Call filter_active_interfaces or filter_complete_interfaces, with parameter full.

    Parameters:
        full (boolean): A queryset of interfaces to perform filter. If true, will perform
        a complete filter with filter_complete_interfaces

    Returns:
        django queryset: Django queryset containing all active interfaces, related with
        a user with valid membership, and with valid assigned ipv4 address

    """
    return all_active_interfaces(full=full).filter(ipv4__isnull=False)


def all_active_interfaces_count():
    """Counts all interfaces of people who have an valid internet access at org.

    Returns:
        int: Number of all active interfaces, related with
        a user with valid membership.

    """
    return Interface.objects.filter(
        machine__in=Machine.objects.filter(user__in=all_has_access()).filter(
            active=True
        )
    )


def all_active_assigned_interfaces_count():
    """Counts all interfaces of people who have an valid internet access at org,
    and with valid ipv4.

    Returns:
        int: Number of all active interfaces, related with
        a user with valid membership, and with valid assigned ipv4 address

    """
    return all_active_interfaces_count().filter(ipv4__isnull=False)


def remove_user_room(room, force=True):
    """Remove the previous user of that room. If force, will not perform a check
    of membership on him before doing it

    Parameters:
        room (Room instance): Room to make free of user
        force (boolean): If true, bypass membership check

    """
    try:
        user = Adherent.objects.get(room=room)
    except Adherent.DoesNotExist:
        return

    if force or not user.has_access():
        user.room = None
        user.save()


def permission_tree(queryset=None):
    r = {}
    permissions = queryset or Permission.objects.all()
    for p in permissions:
        key, app, model = p.natural_key()
        name = p.name
        if app not in r:
            r[app] = {}
        if model not in r[app]:
            r[app][model] = {}
        r[app][model][key] = p
    return r
