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

from cotisations.models import Cotisation, Facture, Vente
from machines.models import Interface, Machine
from users.models import Adherent, User, Ban, Whitelist


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
                ).filter(Q(date_start__lt=search_time) & Q(date_end__gt=search_time))
            )
        )
    ).distinct()


def all_baned(search_time=None):
    """ Fonction renvoyant tous les users bannis """
    if search_time is None:
        search_time = timezone.now()
    return User.objects.filter(
        ban__in=Ban.objects.filter(
            Q(date_start__lt=search_time) & Q(date_end__gt=search_time)
        )
    ).distinct()


def all_whitelisted(search_time=None):
    """ Fonction renvoyant tous les users whitelistes """
    if search_time is None:
        search_time = timezone.now()
    return User.objects.filter(
        whitelist__in=Whitelist.objects.filter(
            Q(date_start__lt=search_time) & Q(date_end__gt=search_time)
        )
    ).distinct()


def all_has_access(search_time=None):
    """  Renvoie tous les users beneficiant d'une connexion
    : user adherent ou whiteliste et non banni """
    if search_time is None:
        search_time = timezone.now()
    return User.objects.filter(
        Q(state=User.STATE_ACTIVE) &
        ~Q(ban__in=Ban.objects.filter(Q(date_start__lt=search_time) & Q(date_end__gt=search_time))) &
        (Q(whitelist__in=Whitelist.objects.filter(Q(date_start__lt=search_time) & Q(date_end__gt=search_time))) |
         Q(facture__in=Facture.objects.filter(
             vente__in=Vente.objects.filter(
                 cotisation__in=Cotisation.objects.filter(
                     Q(type_cotisation='All') | Q(type_cotisation='Connexion'),
                     vente__in=Vente.objects.filter(
                         facture__in=Facture.objects.all()
                         .exclude(valid=False)
                     )
                 ).filter(Q(date_start__lt=search_time) & Q(date_end__gt=search_time))
             )
         )))
    ).distinct()


def filter_active_interfaces(interface_set):
    """Filtre les machines autorisées à sortir sur internet dans une requête"""
    return (interface_set
            .filter(
                machine__in=Machine.objects.filter(
                    user__in=all_has_access()
                ).filter(active=True)
            ).select_related('domain')
            .select_related('machine')
            .select_related('type')
            .select_related('ipv4')
            .select_related('domain__extension')
            .select_related('ipv4__ip_type')
            .distinct())


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


def remove_user_room(room):
    """ Déménage de force l'ancien locataire de la chambre """
    try:
        user = Adherent.objects.get(room=room)
    except Adherent.DoesNotExist:
        return
    user.room = None
    user.save()

