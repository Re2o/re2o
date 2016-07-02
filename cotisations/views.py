# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz
# Gplv2
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader
from django.contrib import messages

from cotisations.models import NewFactureForm, EditFactureForm, Facture, Article

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(template, c, context_instance=RequestContext(request))

def new_facture(request, userid):
    facture = Facture.objects.create(user=userid)
    facture_form = NewFactureForm(request.POST or None, instance=facture)
    if facture_form.is_valid():
        facture_form.save()
        messages.success(request, "La facture a été crée")
        return redirect("/cotisations/")
    return form({'factureform': facture_form}, 'cotisations/facture.html', request)

def edit_facture(request, factureid):
    try:
        facture = Facture.objects.get(pk=factureid)
    except Facture.DoesNotExist:
        messages.error(request, u"Facture inexistante" )
        return redirect("/cotisations/")
    facture_form = EditFactureForm(request.POST or None, instance=facture)
    if facture_form.is_valid():
        facture_form.save()
        messages.success(request, "La facture a bien été modifiée")
        return redirect("/cotisations/")
    return form({'factureform': facture}, 'cotisations/facture.html', request)

def index(request):
    facture_list = Facture.objects.order_by('pk')
    return render(request, 'cotisations/index.html', {'facture_list': facture_list})
