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

from cotisations.models import Cotisation, Facture, Paiement, Vente
from machines.models import Domain, Interface, Machine
from users.models import User, Ban, Whitelist
from preferences.models import Service

DT_NOW = timezone.now()


def all_adherent(search_time=DT_NOW):
    """ Fonction renvoyant tous les users adherents. Optimisee pour n'est
    qu'une seule requete sql
    Inspecte les factures de l'user et ses cotisation, regarde si elles
    sont posterieur à now (end_time)"""
    return User.objects.filter(
        facture__in=Facture.objects.filter(
            vente__in=Vente.objects.filter(
                cotisation__in=Cotisation.objects.filter(
                    vente__in=Vente.objects.filter(
                        facture__in=Facture.objects.all().exclude(valid=False)
                    )
                ).filter(date_end__gt=search_time)
            )
        )
    ).distinct()


def all_baned(search_time=DT_NOW):
    """ Fonction renvoyant tous les users bannis """
    return User.objects.filter(
        ban__in=Ban.objects.filter(
            date_end__gt=search_time
        )
    ).distinct()


def all_whitelisted(search_time=DT_NOW):
    """ Fonction renvoyant tous les users whitelistes """
    return User.objects.filter(
        whitelist__in=Whitelist.objects.filter(
            date_end__gt=search_time
        )
    ).distinct()


def all_has_access(search_time=DT_NOW):
    """  Renvoie tous les users beneficiant d'une connexion
    : user adherent ou whiteliste et non banni """
    return User.objects.filter(
        Q(state=User.STATE_ACTIVE) &
        ~Q(ban__in=Ban.objects.filter(date_end__gt=search_time)) &
        (Q(whitelist__in=Whitelist.objects.filter(date_end__gt=search_time)) |
         Q(facture__in=Facture.objects.filter(
             vente__in=Vente.objects.filter(
                 cotisation__in=Cotisation.objects.filter(
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


def all_active_interfaces():
    """Renvoie l'ensemble des machines autorisées à sortir sur internet """
    return filter_active_interfaces(Interface.objects)


def all_active_assigned_interfaces():
    """ Renvoie l'ensemble des machines qui ont une ipv4 assignées et
    disposant de l'accès internet"""
    return all_active_interfaces().filter(ipv4__isnull=False)


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
        'name': ['name'],
        'surname': ['surname'],
        'pseudo': ['pseudo'],
        'room': ['room'],
        'default': ['state', 'pseudo']
    }
    USERS_INDEX_BAN = {
        'user': ['user__pseudo'],
        'start': ['date_start'],
        'end': ['date_end'],
        'default': ['-date_end']
    }
    USERS_INDEX_WHITE = {
        'user': ['user__pseudo'],
        'start': ['date_start'],
        'end': ['date_end'],
        'default': ['-date_end']
    }
    MACHINES_INDEX = {
        'name': ['name'],
        'default': ['pk']
    }
    COTISATIONS_INDEX = {
        'user': ['user__pseudo'],
        'paiement': ['paiement__moyen'],
        'date': ['date'],
        'default': ['-date']
    }
    COTISATIONS_CONTROL = {
        'name': ['user__name'],
        'surname': ['user__surname'],
        'paiement': ['paiement'],
        'date': ['date'],
        'valid': ['valid'],
        'control': ['control'],
        'default': ['-date']
    }
    TOPOLOGIE_INDEX = {
        'dns': ['switch_interface__domain__name'],
        'ip': ['switch_interface__ipv4__ipv4'],
        'loc': ['location'],
        'ports': ['number'],
        'stack': ['stack__name'],
        'default': ['location', 'stack', 'stack_member_id']
    }
    TOPOLOGIE_INDEX_PORT = {
        'port': ['port'],
        'room': ['room__name'],
        'interface': ['machine_interface__domain__name'],
        'related': ['related__switch__name'],
        'radius': ['radius'],
        'vlan': ['vlan_force__name'],
        'default': ['port']
    }
    TOPOLOGIE_INDEX_ROOM = {
        'name': ['name'],
        'default': ['name']
    }
    TOPOLOGIE_INDEX_STACK = {
        'name': ['name'],
        'id': ['stack_id'],
        'default': ['stack_id'],
    }
    LOGS_INDEX = {
        'date': ['revision__date_created'],
        'default': ['-revision__date_created'],
    }
    LOGS_STATS_LOGS = {
        'author': ['user__name'],
        'date': ['date_created'],
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
        if order == 'desc':
            return request.reverse()
        else:
            return request
