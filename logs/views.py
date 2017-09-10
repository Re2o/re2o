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
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.template.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import Context, RequestContext, loader
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError
from django.forms import ValidationError
from django.db import transaction
from django.db.models import Count

from reversion.models import Revision
from reversion.models import Version

from users.models import User, ServiceUser, Right, School, ListRight, ListShell, Ban, Whitelist
from users.models import all_has_access, all_whitelisted, all_baned, all_adherent
from cotisations.models import Facture, Vente, Article, Banque, Paiement, Cotisation
from machines.models import Machine, MachineType, IpType, Extension, Interface, Domain, IpList
from machines.views import all_active_assigned_interfaces_count, all_active_interfaces_count
from topologie.models import Switch, Port, Room
from preferences.models import GeneralOption

from django.utils import timezone
from dateutil.relativedelta import relativedelta

STATS_DICT = {
        0 : ["Tout", 36],
        1 : ["1 mois", 1],
        2 : ["2 mois", 2],
        3 : ["6 mois", 6],
        4 : ["1 an", 12],
        5 : ["2 an", 24],
}

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render(request, template, c)

@login_required
@permission_required('cableur')
def index(request):
    options, created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number

    revisions = Revision.objects.all().order_by('date_created').reverse().select_related('user').prefetch_related('version_set__object')
    reversions = []
    for revision in revisions :
        for reversion in revision.version_set.all() :
            
            content = ''
            try :
                content = reversion.content_type.name
            except :
            # If reversion has no content_type (when object has been deleted)
                pass

            if content in ['ban', 'whitelist', 'vente', 'cotisation', 'interface', 'user'] :
                reversions.append(
                        {'id' : revision.id,
                            'datetime': revision.date_created.strftime('%d/%m/%y %H:%M:%S'),
                            'username': revision.user.get_username() if revision.user else '?',
                            'user_id': revision.user_id,
                            'rev': reversion }
                        )
                break

    paginator = Paginator(reversions, pagination_number)
    page = request.GET.get('page')
    try:
        reversions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reversions = paginator.page(1)
    except EmptyPage:
     # If page is out of range (e.g. 9999), deliver last page of results.
        reversions = paginator.page(paginator.num_pages)
    return render(request, 'logs/index.html', {'reversions_list': reversions})

@login_required
@permission_required('cableur')
def stats_logs(request):
    options, created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    revisions = Revision.objects.all().order_by('date_created').reverse().select_related('user').prefetch_related('version_set__object')
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
    return render(request, 'logs/stats_logs.html', {'revisions_list': revisions})

@login_required
@permission_required('bureau')
def revert_action(request, revision_id):
    """ Annule l'action en question """
    try:
        revision = Revision.objects.get(id=revision_id)
    except Revision.DoesNotExist:
        messages.error(request, u"Revision inexistante" )
    if request.method == "POST":
        revision.revert()
        messages.success(request, "L'action a été supprimée")
        return redirect("/logs/")
    return form({'objet': revision, 'objet_name': revision.__class__.__name__ }, 'logs/delete.html', request)

@login_required
@permission_required('cableur')
def stats_general(request):
    all_active_users = User.objects.filter(state=User.STATE_ACTIVE)
    ip = dict()
    for ip_range in IpType.objects.all():
        all_ip = IpList.objects.filter(ip_type=ip_range)
        used_ip = Interface.objects.filter(ipv4__in=all_ip).count()
        active_ip = all_active_assigned_interfaces_count().filter(ipv4__in=IpList.objects.filter(ip_type=ip_range)).count()
        ip[ip_range] = [ip_range, all_ip.count(), used_ip, active_ip, all_ip.count()-used_ip]
    stats = [
    [["Categorie", "Nombre d'utilisateurs"], {
    'active_users' : ["Users actifs", User.objects.filter(state=User.STATE_ACTIVE).count()],
    'inactive_users' : ["Users désactivés", User.objects.filter(state=User.STATE_DISABLED).count()],
    'archive_users' : ["Users archivés", User.objects.filter(state=User.STATE_ARCHIVE).count()],
    'adherent_users' : ["Adhérents à l'association", all_adherent().count()],
    'connexion_users' : ["Utilisateurs bénéficiant d'une connexion", all_has_access().count()],
    'ban_users' : ["Utilisateurs bannis", all_baned().count()],
    'whitelisted_user' : ["Utilisateurs bénéficiant d'une connexion gracieuse", all_whitelisted().count()],
    'actives_interfaces' : ["Interfaces actives (ayant accès au reseau)", all_active_interfaces_count().count()],
    'actives_assigned_interfaces' : ["Interfaces actives et assignées ipv4", all_active_assigned_interfaces_count().count()]
    }],
    [["Range d'ip", "Nombre d'ip totales", "Ip assignées", "Ip assignées à une machine active", "Ip non assignées"] ,ip]
    ]
    return render(request, 'logs/stats_general.html', {'stats_list': stats})


@login_required
@permission_required('cableur')
def stats_models(request):
    all_active_users = User.objects.filter(state=User.STATE_ACTIVE)
    stats = {
    'Users' : {
    'users' : [User.PRETTY_NAME, User.objects.count()],
    'serviceuser' : [ServiceUser.PRETTY_NAME, ServiceUser.objects.count()],
    'right' : [Right.PRETTY_NAME, Right.objects.count()],
    'school' : [School.PRETTY_NAME, School.objects.count()],
    'listright' : [ListRight.PRETTY_NAME, ListRight.objects.count()],
    'listshell' : [ListShell.PRETTY_NAME, ListShell.objects.count()],
    'ban' : [Ban.PRETTY_NAME, Ban.objects.count()],
    'whitelist' : [Whitelist.PRETTY_NAME, Whitelist.objects.count()]
    },
    'Cotisations' : {
    'factures' : [Facture.PRETTY_NAME, Facture.objects.count()],
    'vente' : [Vente.PRETTY_NAME, Vente.objects.count()],
    'cotisation' : [Cotisation.PRETTY_NAME, Cotisation.objects.count()],
    'article' : [Article.PRETTY_NAME, Article.objects.count()],
    'banque' : [Banque.PRETTY_NAME, Banque.objects.count()],
    'cotisation' : [Cotisation.PRETTY_NAME, Cotisation.objects.count()],
    },
    'Machines' : {
    'machine' : [Machine.PRETTY_NAME, Machine.objects.count()],
    'typemachine' : [MachineType.PRETTY_NAME, MachineType.objects.count()],
    'typeip' : [IpType.PRETTY_NAME, IpType.objects.count()],
    'extension' : [Extension.PRETTY_NAME, Extension.objects.count()],
    'interface' : [Interface.PRETTY_NAME, Interface.objects.count()],
    'alias' : [Domain.PRETTY_NAME, Domain.objects.exclude(cname=None).count()],
    'iplist' : [IpList.PRETTY_NAME, IpList.objects.count()],
    },
    'Topologie' : {
    'switch' : [Switch.PRETTY_NAME, Switch.objects.count()],
    'port' : [Port.PRETTY_NAME, Port.objects.count()],
    'chambre' : [Room.PRETTY_NAME, Room.objects.count()],
    },
    'Actions effectuées sur la base' : 
    {
    'revision' : ["Nombre d'actions", Revision.objects.count()],
    },
    }
    return render(request, 'logs/stats_models.html', {'stats_list': stats}) 

@login_required
@permission_required('cableur')
def stats_users(request):
    onglet = request.GET.get('onglet')
    try:
        search_field = STATS_DICT[onglet]
    except:
        search_field = STATS_DICT[0]
        onglet = 0
    start_date = timezone.now() + relativedelta(months=-search_field[1])
    stats = {
    'Utilisateur' : {
    'Machines' : User.objects.annotate(num=Count('machine')).order_by('-num')[:10],
    'Facture' : User.objects.annotate(num=Count('facture')).order_by('-num')[:10],
    'Bannissement' : User.objects.annotate(num=Count('ban')).order_by('-num')[:10],
    'Accès gracieux' : User.objects.annotate(num=Count('whitelist')).order_by('-num')[:10],
    'Droits' : User.objects.annotate(num=Count('right')).order_by('-num')[:10],
    },
    'Etablissement' : {
    'Utilisateur' : School.objects.annotate(num=Count('user')).order_by('-num')[:10],
    },
    'Moyen de paiement' : {
    'Utilisateur' : Paiement.objects.annotate(num=Count('facture')).order_by('-num')[:10],
    },
    'Banque' : {
    'Utilisateur' : Banque.objects.annotate(num=Count('facture')).order_by('-num')[:10],
    },
    }
    return render(request, 'logs/stats_users.html', {'stats_list': stats, 'stats_dict' : STATS_DICT, 'active_field': onglet})

@login_required
@permission_required('cableur')
def stats_actions(request):
    onglet = request.GET.get('onglet')
    stats = {
    'Utilisateur' : {
    'Action' : User.objects.annotate(num=Count('revision')).order_by('-num')[:40],
    },
    }
    return render(request, 'logs/stats_users.html', {'stats_list': stats})
