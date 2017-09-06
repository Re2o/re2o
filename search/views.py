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

# App de recherche pour re2o
# Augustin lemesle, Gabriel Détraz, Goulven Kermarec
# Gplv2
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.context_processors import csrf
from django.template import Context, RequestContext, loader
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from users.models import User, Ban, Whitelist
from machines.models import Machine, Interface
from topologie.models import Port, Switch
from cotisations.models import Facture
from search.models import SearchForm, SearchFormPlus
from preferences.models import GeneralOption

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render(request, template, c)

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
    query1 = Q()
    for s in states:
        query1 = query1 | Q(state = s)
    
    connexion = [] 
   
    recherche = {'users_list': None, 'machines_list' : [], 'facture_list' : None, 'ban_list' : None, 'white_list': None, 'port_list': None, 'switch_list': None}

    if request.user.has_perms(('cableur',)):
        query = Q(user__pseudo__icontains = search) | Q(user__name__icontains = search) | Q(user__surname__icontains = search)
    else:
        query = (Q(user__pseudo__icontains = search) | Q(user__name__icontains = search) | Q(user__surname__icontains = search)) & Q(user = request.user)


    for i in aff:
        if i == '0':
            query_user_list = Q(room__name__icontains = search) | Q(pseudo__icontains = search) | Q(name__icontains = search) | Q(surname__icontains = search) & query1
            if request.user.has_perms(('cableur',)):
                recherche['users_list'] = User.objects.filter(query_user_list).order_by('state', 'surname').distinct()
            else :
                recherche['users_list'] = User.objects.filter(query_user_list & Q(id=request.user.id)).order_by('state', 'surname').distinct()
        if i == '1':
            query_machine_list = Q(machine__user__pseudo__icontains = search) | Q(machine__user__name__icontains = search) | Q(machine__user__surname__icontains = search) | Q(mac_address__icontains = search) | Q(ipv4__ipv4__icontains = search) | Q(domain__name__icontains = search) | Q(domain__related_domain__name__icontains = search)
            if request.user.has_perms(('cableur',)):
                data = Interface.objects.filter(query_machine_list).distinct()
            else:
                data = Interface.objects.filter(query_machine_list & Q(machine__user__id = request.user.id)).distinct()
            for d in data:
                  recherche['machines_list'].append(d.machine)
        if i == '2':
            recherche['facture_list'] = Facture.objects.filter(query & date_query).distinct()
        if i == '3':
            recherche['ban_list'] = Ban.objects.filter(query).distinct()
        if i == '4':
            recherche['white_list'] = Whitelist.objects.filter(query).distinct()
        if i == '5':
            recherche['port_list'] = Port.objects.filter(details__icontains = search).distinct()
            if not request.user.has_perms(('cableur',)):
                recherche['port_list'] = None
        if i == '6':
            recherche['switch_list'] = Switch.objects.filter(details__icontains = search).distinct()
            if not request.user.has_perms(('cableur',)):
                recherche['switch_list'] = None
    options, created = GeneralOption.objects.get_or_create()
    search_display_page = options.search_display_page

    for r in recherche:
        if recherche[r] != None:
            recherche[r] = recherche[r][:search_display_page]

    recherche.update({'max_result': search_display_page})

    return recherche

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
