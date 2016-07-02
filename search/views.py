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

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(template, c, context_instance=RequestContext(request))

def search(request):
    if request.method == 'POST':
        search = SearchForm(request.POST or None)
        if search.is_valid():
            search = search.cleaned_data['search_field']
            users = User.objects.filter(Q(pseudo__icontains = search) | Q(name__icontains = search) | Q(surname__icontains = search))
            machines = None
            query = Q(user__pseudo__icontains = search) | Q(user__name__icontains = search) | Q(user__surname__icontains = search)
            factures = Facture.objects.filter(query)
            bans = Ban.objects.filter(query)
            return form({'users_list': users, 'machine_list' : machines, 'facture_list' : factures, 'ban_list' : bans}, 'search/index.html',request)
        return form({'searchform' : search}, 'search/search.html', request)
    else:
        search = SearchForm(request.POST or None) 
        return form({'searchform': search}, 'search/search.html',request)
