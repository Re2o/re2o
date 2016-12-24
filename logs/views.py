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
from cotisations.models import Facture, Vente, Article, Banque, Paiement, Cotisation
from machines.models import Machine, MachineType, IpType, Extension, Interface, Domain, IpList
from topologie.models import Switch, Port, Room

from re2o.settings import PAGINATION_NUMBER, PAGINATION_LARGE_NUMBER

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
    revisions = Revision.objects.all().order_by('date_created').reverse()
    paginator = Paginator(revisions, PAGINATION_NUMBER)
    page = request.GET.get('page')
    try:
        revisions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        revisions = paginator.page(1)
    except EmptyPage:
     # If page is out of range (e.g. 9999), deliver last page of results.
        revisions = paginator.page(paginator.num_pages)
    return render(request, 'logs/index.html', {'revisions_list': revisions})

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
def stats_models(request):
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
