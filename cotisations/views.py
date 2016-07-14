# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz
# Gplv2
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Max, ProtectedError
from django.forms import modelformset_factory, formset_factory
import os

from .models import Facture, Article, Vente, Cotisation, Paiement, Banque
from .forms import NewFactureForm, EditFactureForm, ArticleForm, DelArticleForm, PaiementForm, DelPaiementForm, BanqueForm, DelBanqueForm, NewFactureFormPdf, SelectArticleForm
from users.models import User
from .tex import render_tex
from re2o.settings_local import ASSO_NAME, ASSO_ADDRESS_LINE1, ASSO_ADDRESS_LINE2, ASSO_SIRET, ASSO_EMAIL, ASSO_PHONE, LOGO_PATH
from re2o import settings

from dateutil.relativedelta import relativedelta
from django.utils import timezone

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(template, c, context_instance=RequestContext(request))

def create_cotis(facture, user, duration):
    """ Update et crée l'objet cotisation associé à une facture, prend en argument l'user, la facture pour la quantitéi, et l'article pour la durée"""
    cotisation=Cotisation(facture=facture)
    date_max = user.end_adhesion() or timezone.now()
    if date_max < timezone.now():
        datemax = timezone.now()
    cotisation.date_start=date_max
    cotisation.date_end = cotisation.date_start + relativedelta(months=duration) 
    cotisation.save()
    return

@login_required
@permission_required('cableur')
def new_facture(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, u"Utilisateur inexistant" )
        return redirect("/cotisations/")
    facture = Facture(user=user)
    facture_form = NewFactureForm(request.POST or None, instance=facture)
    article_formset = formset_factory(SelectArticleForm)
    article_formset = article_formset(request.POST or None)
    if facture_form.is_valid() and article_formset.is_valid():
        new_facture = facture_form.save(commit=False)
        articles = article_formset
        if any(art.cleaned_data for art in articles):
            new_facture.save()
            for art_item in articles:
                if art_item.cleaned_data:
                    article = art_item.cleaned_data['article']
                    quantity = art_item.cleaned_data['quantity']
                    new_vente = Vente.objects.create(facture=new_facture, name=article.name, prix=article.prix, cotisation=article.cotisation, duration=article.duration, number=quantity)
                    new_vente.save()
            if any(art.cleaned_data['article'].cotisation for art in articles):
                duration = sum(art.cleaned_data['article'].duration*art.cleaned_data['quantity'] for art in articles if art.cleaned_data['article'].cotisation)
                create_cotis(new_facture, user, duration)
                messages.success(request, "La cotisation a été prolongée pour l'adhérent %s " % user.name )
            else:
                messages.success(request, "La facture a été crée")
            return redirect("/users/profil/" + userid)
        messages.error(request, u"Il faut au moins un article valide pour créer une facture" )
    return form({'factureform': facture_form, 'venteform': article_formset}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def new_facture_pdf(request):
    facture_form = NewFactureFormPdf(request.POST or None)
    if facture_form.is_valid():
        tbl = []
        article = facture_form.cleaned_data['article']
        quantite = facture_form.cleaned_data['number']
        paid = facture_form.cleaned_data['paid']
        destinataire = facture_form.cleaned_data['dest']
        chambre = facture_form.cleaned_data['chambre']
        fid = facture_form.cleaned_data['fid']
        for a in article:
            tbl.append([a, quantite, a.prix * quantite])
        prix_total = sum(a[2] for a in tbl)
        user = {'name':destinataire, 'room':chambre}
        return render_tex(request, 'cotisations/factures.tex', {'DATE' : timezone.now(),'dest':user,'fid':fid, 'article':tbl, 'total':prix_total, 'paid':paid, 'asso_name':ASSO_NAME, 'line1':ASSO_ADDRESS_LINE1, 'line2':ASSO_ADDRESS_LINE2, 'siret':ASSO_SIRET, 'email':ASSO_EMAIL, 'phone':ASSO_PHONE, 'tpl_path': os.path.join(settings.BASE_DIR, LOGO_PATH)})
    return form({'factureform': facture_form}, 'cotisations/facture.html', request) 

@login_required
def facture_pdf(request, factureid):
    try:
        facture = Facture.objects.get(pk=factureid)
    except Facture.DoesNotExist:
        messages.error(request, u"Facture inexistante" )
        return redirect("/cotisations/")
    if not request.user.has_perms(('cableur',)) and facture.user != request.user:
        messages.error(request, "Vous ne pouvez pas afficher une facture ne vous appartenant pas sans droit cableur")
        return redirect("/users/profil/" + str(request.user.id))
    vente = Vente.objects.all().filter(facture=facture)
    ventes = []
    for v in vente:
        ventes.append([v, v.number, v.prix_total])
    return render_tex(request, 'cotisations/factures.tex', {'paid':True, 'fid':facture.id, 'DATE':facture.date,'dest':facture.user, 'article':ventes, 'total': facture.prix_total(), 'asso_name':ASSO_NAME, 'line1': ASSO_ADDRESS_LINE1, 'line2':ASSO_ADDRESS_LINE2, 'siret':ASSO_SIRET, 'email':ASSO_EMAIL, 'phone':ASSO_PHONE, 'tpl_path':os.path.join(settings.BASE_DIR, LOGO_PATH)})

@login_required
@permission_required('cableur')
def edit_facture(request, factureid):
    try:
        facture = Facture.objects.get(pk=factureid)
    except Facture.DoesNotExist:
        messages.error(request, u"Facture inexistante" )
        return redirect("/cotisations/")
    facture_form = EditFactureForm(request.POST or None, instance=facture)
    ventes_objects = Vente.objects.filter(facture=facture)
    vente_form_set = modelformset_factory(Vente, fields=('name','prix','number'), can_delete=True)
    vente_form = vente_form_set(request.POST or None, queryset=ventes_objects)
    if facture_form.is_valid() and vente_form.is_valid():
        facture_form.save()
        vente_form.save()
        messages.success(request, "La facture a bien été modifiée")
        return redirect("/cotisations/")
    return form({'factureform': facture_form, 'venteform': vente_form}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def add_article(request):
    article = ArticleForm(request.POST or None)
    if article.is_valid():
        article.save()
        messages.success(request, "L'article a été ajouté")
        return redirect("/cotisations/index_article/")
    return form({'factureform': article}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def edit_article(request, articleid):
    try:
        article_instance = Article.objects.get(pk=articleid)
    except Article.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/cotisations/index_article/")
    article = ArticleForm(request.POST or None, instance=article_instance)
    if article.is_valid():
        article.save()
        messages.success(request, "Type d'article modifié")
        return redirect("/cotisations/index_article/")
    return form({'factureform': article}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def del_article(request):
    article = DelArticleForm(request.POST or None)
    if article.is_valid():
        article_del = article.cleaned_data['articles']
        article_del.delete()
        messages.success(request, "Le/les articles ont été supprimé")
        return redirect("/cotisations/index_article")
    return form({'factureform': article}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def add_paiement(request):
    paiement = PaiementForm(request.POST or None)
    if paiement.is_valid():
        paiement.save()
        messages.success(request, "Le moyen de paiement a été ajouté")
        return redirect("/cotisations/index_paiement/")
    return form({'factureform': paiement}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def edit_paiement(request, paiementid):
    try:
        paiement_instance = Paiement.objects.get(pk=paiementid)
    except Paiement.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/cotisations/index_paiement/")
    paiement = PaiementForm(request.POST or None, instance=paiement_instance)
    if paiement.is_valid():
        paiement.save()
        messages.success(request, "Type de paiement modifié")
        return redirect("/cotisations/index_paiement/")
    return form({'factureform': paiement}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def del_paiement(request):
    paiement = DelPaiementForm(request.POST or None)
    if paiement.is_valid():
        paiement_dels = paiement.cleaned_data['paiements']
        for paiement_del in paiement_dels:
            try:
                paiement_del.delete()
                messages.success(request, "Le moyen de paiement a été supprimé")
            except ProtectedError:
                messages.error(request, "Le moyen de paiement %s est affecté à au moins une facture, vous ne pouvez pas le supprimer" % paiement_del)
        return redirect("/cotisations/index_paiement/")
    return form({'factureform': paiement}, 'cotisations/facture.html', request)

@login_required
@permission_required('cableur')
def add_banque(request):
    banque = BanqueForm(request.POST or None)
    if banque.is_valid():
        banque.save()
        messages.success(request, "La banque a été ajoutée")
        return redirect("/cotisations/index_banque/")
    return form({'factureform': banque}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def edit_banque(request, banqueid):
    try:
        banque_instance = Article.objects.get(pk=banqueid)
    except Banque.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/cotisations/index_banque/")
    banque = BanqueForm(request.POST or None, instance=banque_instance)
    if banque.is_valid():
        banque.save()
        messages.success(request, "Banque modifiée")
        return redirect("/cotisations/index_banque/")
    return form({'factureform': banque}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def del_banque(request):
    banque = DelBanqueForm(request.POST or None)
    if banque.is_valid():
        banque_dels = banque.cleaned_data['banques']
        for banque_del in banque_dels:
            try:
                banque_del.delete()
                messages.success(request, "La banque a été supprimée")
            except ProtectedError:
                messages.error(request, "La banque %s est affectée à au moins une facture, vous ne pouvez pas la supprimer" % banque_del)
        return redirect("/cotisations/index_banque/")
    return form({'factureform': banque}, 'cotisations/facture.html', request)

@login_required
@permission_required('cableur')
def index_article(request):
    article_list = Article.objects.order_by('name')
    return render(request, 'cotisations/index_article.html', {'article_list':article_list})

@login_required
@permission_required('cableur')
def index_paiement(request):
    paiement_list = Paiement.objects.order_by('moyen')
    return render(request, 'cotisations/index_paiement.html', {'paiement_list':paiement_list})

@login_required
@permission_required('cableur')
def index_banque(request):
    banque_list = Banque.objects.order_by('name')
    return render(request, 'cotisations/index_banque.html', {'banque_list':banque_list})

@login_required
@permission_required('cableur')
def index(request):
    facture_list = Facture.objects.order_by('date').reverse()
    return render(request, 'cotisations/index.html', {'facture_list': facture_list})
