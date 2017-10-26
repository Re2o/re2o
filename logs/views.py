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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count

from reversion.models import Revision
from reversion.models import Version, ContentType

from users.models import User, ServiceUser, Right, School, ListRight, ListShell
from users.models import Ban, Whitelist
from cotisations.models import Facture, Vente, Article, Banque, Paiement
from cotisations.models import Cotisation
from machines.models import Machine, MachineType, IpType, Extension, Interface
from machines.models import Domain, IpList
from topologie.models import Switch, Port, Room
from preferences.models import GeneralOption
from re2o.views import form
from re2o.utils import all_whitelisted, all_baned, all_has_access, all_adherent
from re2o.utils import all_active_assigned_interfaces_count
from re2o.utils import all_active_interfaces_count, SortTable

STATS_DICT = {
    0: ["Tout", 36],
    1: ["1 mois", 1],
    2: ["2 mois", 2],
    3: ["6 mois", 6],
    4: ["1 an", 12],
    5: ["2 an", 24],
}


@login_required
@permission_required('cableur')
def index(request):
    """Affiche les logs affinés, date reformatées, selectionne
    les event importants (ajout de droits, ajout de ban/whitelist)"""
    options, _created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    # The types of content kept for display
    content_type_filter = ['ban', 'whitelist', 'vente', 'interface', 'user']
    # Select only wanted versions
    versions = Version.objects.filter(
        content_type__in=ContentType.objects.filter(
            model__in=content_type_filter
        )
    ).select_related('revision')
    versions = SortTable.sort(
        versions,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.LOGS_INDEX
    )
    paginator = Paginator(versions, pagination_number)
    page = request.GET.get('page')
    try:
        versions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        versions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        versions = paginator.page(paginator.num_pages)

    # Force to have a list instead of QuerySet
    versions.count(0)
    # Items to remove later because invalid
    to_remove = []
    # Parse every item (max = pagination_number)
    for i in range(len(versions.object_list)):
        if versions.object_list[i].object:
            version = versions.object_list[i]
            versions.object_list[i] = {
                'rev_id': version.revision.id,
                'comment': version.revision.comment,
                'datetime': version.revision.date_created.strftime(
                    '%d/%m/%y %H:%M:%S'
                    ),
                'username':
                    version.revision.user.get_username()
                    if version.revision.user else '?',
                'user_id': version.revision.user_id,
                'version': version}
        else:
            to_remove.insert(0, i)
    # Remove all tagged invalid items
    for i in to_remove:
        versions.object_list.pop(i)
    return render(request, 'logs/index.html', {'versions_list': versions})


@login_required
@permission_required('cableur')
def stats_logs(request):
    """Affiche l'ensemble des logs et des modifications sur les objets,
    classés par date croissante, en vrac"""
    options, _created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    revisions = Revision.objects.all().select_related('user')\
        .prefetch_related('version_set__object')
    revisions = SortTable.sort(
        revisions,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.LOGS_STATS_LOGS
    )
    paginator = Paginator(revisions, pagination_number)
    page = request.GET.get('page')
    try:
        revisions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        revisions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        revisions = paginator.page(paginator.num_pages)
    return render(request, 'logs/stats_logs.html', {
        'revisions_list': revisions
        })


@login_required
@permission_required('bureau')
def revert_action(request, revision_id):
    """ Annule l'action en question """
    try:
        revision = Revision.objects.get(id=revision_id)
    except Revision.DoesNotExist:
        messages.error(request, u"Revision inexistante")
    if request.method == "POST":
        revision.revert()
        messages.success(request, "L'action a été supprimée")
        return redirect(reverse('logs:index'))
    return form({
        'objet': revision,
        'objet_name': revision.__class__.__name__
        }, 'logs/delete.html', request)


@login_required
@permission_required('cableur')
def stats_general(request):
    """Statistiques générales affinées sur les ip, activées, utilisées par
    range, et les statistiques générales sur les users : users actifs,
    cotisants, activés, archivés, etc"""
    ip_dict = dict()
    for ip_range in IpType.objects.all():
        all_ip = IpList.objects.filter(ip_type=ip_range)
        used_ip = Interface.objects.filter(ipv4__in=all_ip).count()
        active_ip = all_active_assigned_interfaces_count().filter(
            ipv4__in=IpList.objects.filter(ip_type=ip_range)
        ).count()
        ip_dict[ip_range] = [ip_range, all_ip.count(),
                             used_ip, active_ip, all_ip.count()-used_ip]
    stats = [
        [["Categorie", "Nombre d'utilisateurs"], {
            'active_users': [
                "Users actifs",
                User.objects.filter(state=User.STATE_ACTIVE).count()],
            'inactive_users': [
                "Users désactivés",
                User.objects.filter(state=User.STATE_DISABLED).count()],
            'archive_users': [
                "Users archivés",
                User.objects.filter(state=User.STATE_ARCHIVE).count()],
            'adherent_users': [
                "Adhérents à l'association",
                all_adherent().count()],
            'connexion_users': [
                "Utilisateurs bénéficiant d'une connexion",
                all_has_access().count()],
            'ban_users': [
                "Utilisateurs bannis",
                all_baned().count()],
            'whitelisted_user': [
                "Utilisateurs bénéficiant d'une connexion gracieuse",
                all_whitelisted().count()],
            'actives_interfaces': [
                "Interfaces actives (ayant accès au reseau)",
                all_active_interfaces_count().count()],
            'actives_assigned_interfaces': [
                "Interfaces actives et assignées ipv4",
                all_active_assigned_interfaces_count().count()]
        }],
        [["Range d'ip", "Nombre d'ip totales", "Ip assignées",
          "Ip assignées à une machine active", "Ip non assignées"], ip_dict]
        ]
    return render(request, 'logs/stats_general.html', {'stats_list': stats})


@login_required
@permission_required('cableur')
def stats_models(request):
    """Statistiques générales, affiche les comptages par models:
    nombre d'users, d'écoles, de droits, de bannissements,
    de factures, de ventes, de banque, de machines, etc"""
    stats = {
        'Users': {
            'users': [User.PRETTY_NAME, User.objects.count()],
            'serviceuser': [ServiceUser.PRETTY_NAME,
                            ServiceUser.objects.count()],
            'right': [Right.PRETTY_NAME, Right.objects.count()],
            'school': [School.PRETTY_NAME, School.objects.count()],
            'listright': [ListRight.PRETTY_NAME, ListRight.objects.count()],
            'listshell': [ListShell.PRETTY_NAME, ListShell.objects.count()],
            'ban': [Ban.PRETTY_NAME, Ban.objects.count()],
            'whitelist': [Whitelist.PRETTY_NAME, Whitelist.objects.count()]
        },
        'Cotisations': {
            'factures': [Facture.PRETTY_NAME, Facture.objects.count()],
            'vente': [Vente.PRETTY_NAME, Vente.objects.count()],
            'cotisation': [Cotisation.PRETTY_NAME, Cotisation.objects.count()],
            'article': [Article.PRETTY_NAME, Article.objects.count()],
            'banque': [Banque.PRETTY_NAME, Banque.objects.count()],
        },
        'Machines': {
            'machine': [Machine.PRETTY_NAME, Machine.objects.count()],
            'typemachine': [MachineType.PRETTY_NAME,
                            MachineType.objects.count()],
            'typeip': [IpType.PRETTY_NAME, IpType.objects.count()],
            'extension': [Extension.PRETTY_NAME, Extension.objects.count()],
            'interface': [Interface.PRETTY_NAME, Interface.objects.count()],
            'alias': [Domain.PRETTY_NAME,
                      Domain.objects.exclude(cname=None).count()],
            'iplist': [IpList.PRETTY_NAME, IpList.objects.count()],
        },
        'Topologie': {
            'switch': [Switch.PRETTY_NAME, Switch.objects.count()],
            'port': [Port.PRETTY_NAME, Port.objects.count()],
            'chambre': [Room.PRETTY_NAME, Room.objects.count()],
        },
        'Actions effectuées sur la base':
        {
            'revision': ["Nombre d'actions", Revision.objects.count()],
        },
    }
    return render(request, 'logs/stats_models.html', {'stats_list': stats})


@login_required
@permission_required('cableur')
def stats_users(request):
    """Affiche les statistiques base de données aggrégées par user :
    nombre de machines par user, d'etablissements par user,
    de moyens de paiements par user, de banque par user,
    de bannissement par user, etc"""
    onglet = request.GET.get('onglet')
    try:
        _search_field = STATS_DICT[onglet]
    except KeyError:
        _search_field = STATS_DICT[0]
        onglet = 0
    stats = {
        'Utilisateur': {
            'Machines': User.objects.annotate(
                num=Count('machine')
            ).order_by('-num')[:10],
            'Facture': User.objects.annotate(
                num=Count('facture')
            ).order_by('-num')[:10],
            'Bannissement': User.objects.annotate(
                num=Count('ban')
            ).order_by('-num')[:10],
            'Accès gracieux': User.objects.annotate(
                num=Count('whitelist')
            ).order_by('-num')[:10],
            'Droits': User.objects.annotate(
                num=Count('right')
            ).order_by('-num')[:10],
        },
        'Etablissement': {
            'Utilisateur': School.objects.annotate(
                num=Count('user')
            ).order_by('-num')[:10],
        },
        'Moyen de paiement': {
            'Utilisateur': Paiement.objects.annotate(
                num=Count('facture')
            ).order_by('-num')[:10],
        },
        'Banque': {
            'Utilisateur': Banque.objects.annotate(
                num=Count('facture')
            ).order_by('-num')[:10],
        },
    }
    return render(request, 'logs/stats_users.html', {
        'stats_list': stats,
        'stats_dict': STATS_DICT,
        'active_field': onglet
        })


@login_required
@permission_required('cableur')
def stats_actions(request):
    """Vue qui affiche les statistiques de modifications d'objets par
    utilisateurs.
    Affiche le nombre de modifications aggrégées par utilisateurs"""
    stats = {
        'Utilisateur': {
            'Action': User.objects.annotate(
                num=Count('revision')
            ).order_by('-num')[:40],
        },
    }
    return render(request, 'logs/stats_users.html', {'stats_list': stats})
