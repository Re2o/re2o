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

# -*- coding: utf-8 -*-
# David Sinquin, Gabriel Détraz, Goulven Kermarec
"""
Regroupe les fonctions transversales utiles

Fonction :
    - récupérer tous les utilisateurs actifs
    - récupérer toutes les machines
    - récupérer tous les bans
    etc
"""


from __future__ import unicode_literals


from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from cotisations.models import Cotisation, Facture, Paiement, Vente
from machines.models import Domain, Interface, Machine
from users.models import Adherent, User, Ban, Whitelist
from preferences.models import Service


def all_adherent(search_time=None):
    """ Fonction renvoyant tous les users adherents. Optimisee pour n'est
    qu'une seule requete sql
    Inspecte les factures de l'user et ses cotisation, regarde si elles
    sont posterieur à now (end_time)"""
    if search_time is None:
        search_time = timezone.now()
    return User.objects.filter(
        facture__in=Facture.objects.filter(
            vente__in=Vente.objects.filter(
                Q(type_cotisation='All') | Q(type_cotisation='Adhesion'),
                cotisation__in=Cotisation.objects.filter(
                    vente__in=Vente.objects.filter(
                        facture__in=Facture.objects.all().exclude(valid=False)
                    )
                ).filter(date_end__gt=search_time)
            )
        )
    ).distinct()


def all_baned(search_time=None):
    """ Fonction renvoyant tous les users bannis """
    if search_time is None:
        search_time = timezone.now()
    return User.objects.filter(
        ban__in=Ban.objects.filter(
            date_end__gt=search_time
        )
    ).distinct()


def all_whitelisted(search_time=None):
    """ Fonction renvoyant tous les users whitelistes """
    if search_time is None:
        search_time = timezone.now()
    return User.objects.filter(
        whitelist__in=Whitelist.objects.filter(
            date_end__gt=search_time
        )
    ).distinct()


def all_has_access(search_time=None):
    """  Renvoie tous les users beneficiant d'une connexion
    : user adherent ou whiteliste et non banni """
    if search_time is None:
        search_time = timezone.now()
    return User.objects.filter(
        Q(state=User.STATE_ACTIVE) &
        ~Q(ban__in=Ban.objects.filter(date_end__gt=search_time)) &
        (Q(whitelist__in=Whitelist.objects.filter(date_end__gt=search_time)) |
         Q(facture__in=Facture.objects.filter(
             vente__in=Vente.objects.filter(
                 cotisation__in=Cotisation.objects.filter(
                     Q(type_cotisation='All') | Q(type_cotisation='Connexion'),
                     vente__in=Vente.objects.filter(
                         facture__in=Facture.objects.all()
                         .exclude(valid=False)
                     )
                 ).filter(date_end__gt=search_time)
             )
         )))
    ).distinct()


def filter_active_interfaces(interface_set):
    """Filtre les machines autorisées à sortir sur internet dans une requête"""
    return interface_set.filter(
        machine__in=Machine.objects.filter(
            user__in=all_has_access()
        ).filter(active=True)
    ).select_related('domain').select_related('machine')\
    .select_related('type').select_related('ipv4')\
    .select_related('domain__extension').select_related('ipv4__ip_type')\
    .distinct()


def filter_complete_interfaces(interface_set):
    """Appel la fonction précédente avec un prefetch_related ipv6 en plus"""
    return filter_active_interfaces(interface_set).prefetch_related('ipv6list')


def all_active_interfaces(full=False):
    """Renvoie l'ensemble des machines autorisées à sortir sur internet """
    if full:
        return filter_complete_interfaces(Interface.objects)
    else:
        return filter_active_interfaces(Interface.objects)


def all_active_assigned_interfaces(full=False):
    """ Renvoie l'ensemble des machines qui ont une ipv4 assignées et
    disposant de l'accès internet"""
    return all_active_interfaces(full=full).filter(ipv4__isnull=False)


def all_active_interfaces_count():
    """ Version light seulement pour compter"""
    return Interface.objects.filter(
        machine__in=Machine.objects.filter(
            user__in=all_has_access()
        ).filter(active=True)
    )


def all_active_assigned_interfaces_count():
    """ Version light seulement pour compter"""
    return all_active_interfaces_count().filter(ipv4__isnull=False)

class SortTable:
    """ Class gathering uselful stuff to sort the colums of a table, according
    to the column and order requested. It's used with a dict of possible
    values and associated model_fields """

    # All the possible possible values
    # The naming convention is based on the URL or the views function
    # The syntax to describe the sort to apply is a dict where the keys are
    # the url value and the values are a list of model field name to use to
    # order the request. They are applied in the order they are given.
    # A 'default' might be provided to specify what to do if the requested col
    # doesn't match any keys.
    USERS_INDEX = {
        'user_name': ['name'],
        'user_surname': ['surname'],
        'user_pseudo': ['pseudo'],
        'user_room': ['room'],
        'default': ['state', 'pseudo']
    }
    USERS_INDEX_BAN = {
        'ban_user': ['user__pseudo'],
        'ban_start': ['date_start'],
        'ban_end': ['date_end'],
        'default': ['-date_end']
    }
    USERS_INDEX_WHITE = {
        'white_user': ['user__pseudo'],
        'white_start': ['date_start'],
        'white_end': ['date_end'],
        'default': ['-date_end']
    }
    USERS_INDEX_SCHOOL = {
        'school_name': ['name'],
        'default': ['name']
    }
    MACHINES_INDEX = {
        'machine_name': ['name'],
        'default': ['pk']
    }
    COTISATIONS_INDEX = {
        'cotis_user': ['user__pseudo'],
        'cotis_paiement': ['paiement__moyen'],
        'cotis_date': ['date'],
        'cotis_id': ['id'],
        'default': ['-date']
    }
    COTISATIONS_CONTROL = {
        'control_name': ['user__adherent__name'],
        'control_surname': ['user__surname'],
        'control_paiement': ['paiement'],
        'control_date': ['date'],
        'control_valid': ['valid'],
        'control_control': ['control'],
        'control_id': ['id'],
        'control_user-id': ['user__id'],
        'default': ['-date']
    }
    TOPOLOGIE_INDEX = {
        'switch_dns': ['interface__domain__name'],
        'switch_ip': ['interface__ipv4__ipv4'],
        'switch_loc': ['location'],
        'switch_ports': ['number'],
        'switch_stack': ['stack__name'],
        'default': ['location', 'stack', 'stack_member_id']
    }
    TOPOLOGIE_INDEX_PORT = {
        'port_port': ['port'],
        'port_room': ['room__name'],
        'port_interface': ['machine_interface__domain__name'],
        'port_related': ['related__switch__name'],
        'port_radius': ['radius'],
        'port_vlan': ['vlan_force__name'],
        'default': ['port']
    }
    TOPOLOGIE_INDEX_ROOM = {
        'room_name': ['name'],
        'default': ['name']
    }
    TOPOLOGIE_INDEX_BUILDING = {
        'building_name': ['name'],
        'default': ['name']
    }
    TOPOLOGIE_INDEX_BORNE = {
        'ap_name': ['interface__domain__name'],
        'ap_ip': ['interface__ipv4__ipv4'],
        'ap_mac': ['interface__mac_address'],
        'default': ['interface__domain__name']
    }
    TOPOLOGIE_INDEX_STACK = {
        'stack_name': ['name'],
        'stack_id': ['stack_id'],
        'default': ['stack_id'],
    }
    TOPOLOGIE_INDEX_MODEL_SWITCH = {
        'model-switch_name': ['reference'],
        'model-switch_contructor' : ['constructor__name'],
        'default': ['reference'],
    }
    TOPOLOGIE_INDEX_SWITCH_BAY = {
        'switch-bay_name': ['name'],
        'switch-bay_building': ['building__name'],
        'default': ['name'],
    }
    TOPOLOGIE_INDEX_CONSTRUCTOR_SWITCH = {
        'constructor-switch_name': ['name'],
        'default': ['name'],
    }
    LOGS_INDEX = {
        'sum_date': ['revision__date_created'],
        'default': ['-revision__date_created'],
    }
    LOGS_STATS_LOGS = {
        'logs_author': ['user__name'],
        'logs_date': ['date_created'],
        'default': ['-date_created']
    }

    @staticmethod
    def sort(request, col, order, values):
        """ Check if the given values are possible and add .order_by() and
        a .reverse() as specified according to those values """
        fields = values.get(col, None)
        if not fields:
            fields = values.get('default', [])
        request = request.order_by(*fields)
        if values.get(col, None) and order == 'desc':
            return request.reverse()
        else:
            return request

def re2o_paginator(request, query_set, pagination_number):
    """Paginator script for list display in re2o.
    :request:
    :query_set: Query_set to paginate
    :pagination_number: Number of entries to display"""
    paginator = Paginator(query_set, pagination_number)
    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)
    return results

def remove_user_room(room):
    """ Déménage de force l'ancien locataire de la chambre """
    try:
        user = Adherent.objects.get(room=room)
    except Adherent.DoesNotExist:
        return
    user.room = None
    user.save()
