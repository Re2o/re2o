# App de recherche pour re2o
# Gabriel Détraz, Goulven Kermarec
# Gplv2
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader

from django.db.models import Q
from users.models import User, Ban, Whitelist
from machines.models import Machine, Interface
from topologie.models import Port, Switch
from cotisations.models import Facture
from search.models import SearchForm, SearchFormPlus
from users.views import has_access
from cotisations.views import end_adhesion

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(template, c, context_instance=RequestContext(request))

def search_result(search, type):
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
            users = User.objects.filter((Q(pseudo__icontains = search) | Q(name__icontains = search) | Q(surname__icontains = search)) & query)
            connexion = []
            for user in users:
                end=end_adhesion(user)
                access=has_access(user)
                if(len(co)==0 or (len(co)==1 and bool(co[0])==access) or (len(co)==2 and (bool(co[0])==access or bool(co[1])==access))):
                    if(end!=None):
                        connexion.append([user, access, end])
                    else:
                        connexion.append([user, access, "Non adhérent"])
        query = Q(user__pseudo__icontains = search) | Q(user__name__icontains = search) | Q(user__surname__icontains = search)
        if i == '1':
            machines = Interface.objects.filter(machine=Machine.objects.filter(query)) | Interface.objects.filter(Q(dns__icontains = search))
        if i == '2':   
            factures = Facture.objects.filter(query & date_query)
        if i == '3':    
            bans = Ban.objects.filter(query)
        if i == '4':    
            whitelists = Whitelist.objects.filter(query)
        if i == '5':    
            portlist = Port.objects.filter(details__icontains = search)
        if i == '6':    
            switchlist = Switch.objects.filter(details__icontains = search)
    return {'users_list': connexion, 'interfaces_list' : machines, 'facture_list' : factures, 'ban_list' : bans, 'white_list': whitelists, 'port_list':portlist, 'switch_list':switchlist}

def search(request):
    if request.method == 'POST':
        search = SearchForm(request.POST or None)
        if search.is_valid():
            return form(search_result(search, False), 'search/index.html',request)
        return form({'searchform' : search}, 'search/search.html', request)
    else:
        search = SearchForm(request.POST or None) 
        return form({'searchform': search}, 'search/search.html',request)

def searchp(request):
    if request.method == 'POST':
        search = SearchFormPlus(request.POST or None)
        if search.is_valid():
            return form(search_result(search, True), 'search/index.html',request)
        return form({'searchform' : search}, 'search/search.html', request)
    else:
        search = SearchFormPlus(request.POST or None) 
        return form({'searchform': search}, 'search/search.html',request)
