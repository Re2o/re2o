# App de recherche pour re2o
# Gabriel Détraz, Goulven Kermarec
# Gplv2
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader

from django.db.models import Q
from users.models import User, Ban
from machines.models import Machine
from cotisations.models import Facture
from search.models import SearchForm
from users.views import has_access

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(template, c, context_instance=RequestContext(request))

def search(request):
    if request.method == 'POST':
        search = SearchForm(request.POST or None)
        if search.is_valid():
            states = search.cleaned_data['filtre']
            search = search.cleaned_data['search_field']
            query = Q() 
            for s in states:
                query = query | Q(state = s)
            users = User.objects.filter((Q(pseudo__icontains = search) | Q(name__icontains = search) | Q(surname__icontains = search)) & query)
            connexion = []
            for user in users:
                connexion.append([user, has_access(user)])
            machines = None
            query = Q(user__pseudo__icontains = search) | Q(user__name__icontains = search) | Q(user__surname__icontains = search)
            factures = Facture.objects.filter(query)
            bans = Ban.objects.filter(query)
            return form({'users_list': connexion, 'machine_list' : machines, 'facture_list' : factures, 'ban_list' : bans}, 'search/index.html',request)
        return form({'searchform' : search}, 'search/search.html', request)
    else:
        search = SearchForm(request.POST or None) 
        return form({'searchform': search}, 'search/search.html',request)
