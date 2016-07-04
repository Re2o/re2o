# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz
# Gplv2
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader
from django.contrib import messages
from django.db.models import Max

from cotisations.models import NewFactureForm, EditFactureForm, Facture, Article, Cotisation
from users.models import User

from dateutil.relativedelta import relativedelta
from django.utils import timezone

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(template, c, context_instance=RequestContext(request))

def end_adhesion(user):
    """ Renvoie la date de fin d'adhésion d'un user, False sinon """
    date_max = Cotisation.objects.all().filter(facture=Facture.objects.all().filter(user=user).exclude(valid=False)).aggregate(Max('date_end'))['date_end__max']
    return date_max

def is_adherent(user):
    """ Renvoie si un user est à jour de cotisation """
    end = end_adhesion(user)
    if not end:
        return False
    elif end < timezone.now():
        return False
    else:
        return True

def create_cotis(facture, user, article):
    """ Update et crée l'objet cotisation associé à une facture, prend en argument l'user, la facture pour la quantitéi, et l'article pour la durée"""
    cotisation=Cotisation(facture=facture)
    date_max = end_adhesion(user) or timezone.now()
    if date_max < timezone.now():
        datemax = timezone.now()
    cotisation.date_start=date_max
    cotisation.date_end = cotisation.date_start + relativedelta(months=article[0].duration*facture.number) 
    cotisation.save()
    return

def new_facture(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, u"Utilisateur inexistant" )
        return redirect("/cotisations/")
    facture = Facture(user=user)
    facture_form = NewFactureForm(request.POST or None, instance=facture)
    if facture_form.is_valid():
        new_facture = facture_form.save(commit=False)
        article = facture_form.cleaned_data['article']
        new_facture.prix = article[0].prix
        new_facture.name = article[0].name
        new_facture.save()
        if article[0].cotisation == True:
            create_cotis(new_facture, user, article)
            messages.success(request, "La cotisation a été prolongée pour l'adhérent %s " % user.name )
        else:
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
    return form({'factureform': facture_form}, 'cotisations/facture.html', request)

def index(request):
    facture_list = Facture.objects.order_by('pk')
    return render(request, 'cotisations/index.html', {'facture_list': facture_list})
