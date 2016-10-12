# App de recherche pour re2o
# Augustin lemesle, Gabriel Détraz, Goulven Kermarec
# Gplv2
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from users.models import User, Ban, Whitelist
from machines.models import Machine, Interface
from topologie.models import Port, Switch
from cotisations.models import Facture
from search.models import SearchForm, SearchFormPlus

from re2o.settings import SEARCH_RESULT

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(template, c, context_instance=RequestContext(request))

def search_result(search, type, request):
    date_deb = None
    date_fin = None 
    states=[]
    co=[]
    aff=[]
    if(type):
        aff = search.cleaned_data['affichage']
        co = search.cleaned_data['connexion']
        states = search.cleaned_data['filtre']
        date_deb = search.cleaned_data['date_deb']
        date_fin = search.cleaned_data['date_fin']
    date_query = Q()
    if aff==[]:
        aff = ['0','1','2','3','4','5','6']
    if date_deb != None:
        date_query = date_query & Q(date__gte=date_deb)
    if date_fin != None:
        date_query = date_query & Q(date__lte=date_fin)
    search = search.cleaned_data['search_field']
    query = Q() 
    for s in states:
        query = query | Q(state = s)
    
    users = None
    machines = None
    factures = None
    bans = None
    whitelists = None
    switchlist = None
    portlist = None
    connexion = []

    for i in aff:
        if i == '0':
            users = User.objects.filter((Q(pseudo__icontains = search) | Q(name__icontains = search) | Q(surname__icontains = search)) & query)[:SEARCH_RESULT]
        query = Q(user__pseudo__icontains = search) | Q(user__name__icontains = search) | Q(user__surname__icontains = search)
        if i == '1':
            machines = Machine.objects.filter(query)[:SEARCH_RESULT]
        if i == '2':   
            factures = Facture.objects.filter(query & date_query)[:SEARCH_RESULT]
        if i == '3':    
            bans = Ban.objects.filter(query)[:SEARCH_RESULT]
        if i == '4':    
            whitelists = Whitelist.objects.filter(query)[:SEARCH_RESULT]
        if i == '5':    
            portlist = Port.objects.filter(details__icontains = search)[:SEARCH_RESULT]
        if i == '6':    
            switchlist = Switch.objects.filter(details__icontains = search)[:SEARCH_RESULT]
    return {'users_list': users, 'machines_list' : machines, 'facture_list' : factures, 'ban_list' : bans, 'white_list': whitelists, 'port_list':portlist, 'switch_list':switchlist, 'max_result' : SEARCH_RESULT}

@login_required
def search(request):
    search = SearchForm(request.POST or None)
    if search.is_valid():
        return form(search_result(search, False, request), 'search/index.html',request)
    return form({'searchform' : search}, 'search/search.html', request)

@login_required
def searchp(request):
    search = SearchFormPlus(request.POST or None)
    if search.is_valid():
        return form(search_result(search, True, request), 'search/index.html',request)
    return form({'searchform' : search}, 'search/search.html', request)
