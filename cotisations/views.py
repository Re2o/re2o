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

# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz
# Gplv2
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.template.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import Context, RequestContext, loader
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Max, ProtectedError
from django.db import transaction
from django.forms import modelformset_factory, formset_factory
import os
from reversion import revisions as reversion
from reversion.models import Version

from .models import Facture, Article, Vente, Cotisation, Paiement, Banque
from .forms import NewFactureForm, TrezEditFactureForm, EditFactureForm, ArticleForm, DelArticleForm, PaiementForm, DelPaiementForm, BanqueForm, DelBanqueForm, NewFactureFormPdf, CreditSoldeForm, SelectArticleForm
from users.models import User
from .tex import render_tex
from re2o.settings import ASSO_NAME, ASSO_ADDRESS_LINE1, ASSO_ADDRESS_LINE2, ASSO_SIRET, ASSO_EMAIL, ASSO_PHONE, LOGO_PATH
from re2o import settings
from preferences.models import OptionalUser, GeneralOption

from dateutil.relativedelta import relativedelta
from django.utils import timezone

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render(request, template, c)

def create_cotis(vente, user, duration, date_start=False):
    """ Update et crée l'objet cotisation associé à une facture, prend en argument l'user, la facture pour la quantitéi, et l'article pour la durée"""
    cotisation=Cotisation(vente=vente)
    if date_start:
        end_adhesion = Cotisation.objects.filter(vente__in=Vente.objects.filter(facture__in=Facture.objects.filter(user=user).exclude(valid=False))).filter(date_start__lt=date_start).aggregate(Max('date_end'))['date_end__max']
    else:
        end_adhesion = user.end_adhesion()
    date_start = date_start or timezone.now()
    end_adhesion = end_adhesion or date_start
    date_max = max(end_adhesion, date_start)
    cotisation.date_start = date_max
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
    # Le template a besoin de connaitre les articles pour le js
    article_list = Article.objects.all()
    # On envoie la form fature et un formset d'articles
    facture_form = NewFactureForm(request.POST or None, instance=facture)
    article_formset = formset_factory(SelectArticleForm)(request.POST or None)
    if facture_form.is_valid() and article_formset.is_valid():
        new_facture = facture_form.save(commit=False)
        articles = article_formset
        # Si au moins un article est rempli
        if any(art.cleaned_data for art in articles):
            options, created = OptionalUser.objects.get_or_create()
            user_solde = options.user_solde
            solde_negatif = options.solde_negatif
            # Si on paye par solde, que l'option est activée, on vérifie que le négatif n'est pas atteint
            if user_solde:
                if new_facture.paiement == Paiement.objects.get_or_create(moyen='solde')[0]:
                    prix_total = 0
                    for art_item in articles:
                        if art_item.cleaned_data:
                            prix_total += art_item.cleaned_data['article'].prix*art_item.cleaned_data['quantity']
                    if float(user.solde) - float(prix_total) < solde_negatif:
                        messages.error(request, "Le solde est insuffisant pour effectuer l'opération")
                        return redirect("/users/profil/" + userid)
            with transaction.atomic(), reversion.create_revision():
                new_facture.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            for art_item in articles:
                if art_item.cleaned_data:
                    article = art_item.cleaned_data['article']
                    quantity = art_item.cleaned_data['quantity']
                    new_vente = Vente.objects.create(facture=new_facture, name=article.name, prix=article.prix, iscotisation=article.iscotisation, duration=article.duration, number=quantity)
                    with transaction.atomic(), reversion.create_revision():
                        new_vente.save()
                        reversion.set_user(request.user)
                        reversion.set_comment("Création")
                    if art_item.cleaned_data['article'].iscotisation:
                        create_cotis(new_vente, user, art_item.cleaned_data['article'].duration*art_item.cleaned_data['quantity'])
            if any(art_item.cleaned_data['article'].iscotisation for art_item in articles if art_item.cleaned_data):
                messages.success(request, "La cotisation a été prolongée pour l'adhérent %s jusqu'au %s" % (user.pseudo, user.end_adhesion()) )
            else:
                messages.success(request, "La facture a été crée")
            return redirect("/users/profil/" + userid)
        messages.error(request, u"Il faut au moins un article valide pour créer une facture" )
    return form({'factureform': facture_form, 'venteform': article_formset, 'articlelist': article_list}, 'cotisations/new_facture.html', request)

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
    if not facture.valid:
        messages.error(request, "Vous ne pouvez pas afficher une facture non valide")
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
    if request.user.has_perms(['trésorier']):
        facture_form = TrezEditFactureForm(request.POST or None, instance=facture)
    elif facture.control or not facture.valid:
        messages.error(request, "Vous ne pouvez pas editer une facture controlée ou invalidée par le trésorier")
        return redirect("/cotisations/")
    else:
        facture_form = EditFactureForm(request.POST or None, instance=facture)
    ventes_objects = Vente.objects.filter(facture=facture)
    vente_form_set = modelformset_factory(Vente, fields=('name','number'), extra=0, max_num=len(ventes_objects))
    vente_form = vente_form_set(request.POST or None, queryset=ventes_objects)
    if facture_form.is_valid() and vente_form.is_valid():
        with transaction.atomic(), reversion.create_revision():
            facture_form.save()
            vente_form.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for form in vente_form for field in facture_form.changed_data + form.changed_data))
        messages.success(request, "La facture a bien été modifiée")
        return redirect("/cotisations/")
    return form({'factureform': facture_form, 'venteform': vente_form}, 'cotisations/edit_facture.html', request)

@login_required
@permission_required('cableur')
def del_facture(request, factureid):
    try:
        facture = Facture.objects.get(pk=factureid)
    except Facture.DoesNotExist:
        messages.error(request, u"Facture inexistante" )
        return redirect("/cotisations/")
    if (facture.control or not facture.valid):
        messages.error(request, "Vous ne pouvez pas editer une facture controlée ou invalidée par le trésorier")
        return redirect("/cotisations/")
    if request.method == "POST":
        with transaction.atomic(), reversion.create_revision():
            facture.delete()
            reversion.set_user(request.user)
        messages.success(request, "La facture a été détruite")
        return redirect("/cotisations/")
    return form({'objet': facture, 'objet_name': 'facture'}, 'cotisations/delete.html', request)

@login_required
@permission_required('cableur')
def credit_solde(request, userid):
    """ Credit ou débit de solde """
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, u"Utilisateur inexistant" )
        return redirect("/cotisations/")
    facture = CreditSoldeForm(request.POST or None)
    if facture.is_valid():
        facture_instance = facture.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            facture_instance.user = user
            facture_instance.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création") 
        new_vente = Vente.objects.create(facture=facture_instance, name="solde", prix=facture.cleaned_data['montant'], iscotisation=False, duration=0, number=1)
        with transaction.atomic(), reversion.create_revision():
            new_vente.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Solde modifié")
        return redirect("/cotisations/")
    return form({'factureform': facture}, 'cotisations/facture.html', request)


@login_required
@permission_required('trésorier')
def add_article(request):
    article = ArticleForm(request.POST or None)
    if article.is_valid():
        with transaction.atomic(), reversion.create_revision():
            article.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
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
        with transaction.atomic(), reversion.create_revision():
            article.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in article.changed_data))
        messages.success(request, "Type d'article modifié")
        return redirect("/cotisations/index_article/")
    return form({'factureform': article}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def del_article(request):
    article = DelArticleForm(request.POST or None)
    if article.is_valid():
        article_del = article.cleaned_data['articles']
        with transaction.atomic(), reversion.create_revision():
            article_del.delete()
            reversion.set_user(request.user)
        messages.success(request, "Le/les articles ont été supprimé")
        return redirect("/cotisations/index_article")
    return form({'factureform': article}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def add_paiement(request):
    paiement = PaiementForm(request.POST or None)
    if paiement.is_valid():
        with transaction.atomic(), reversion.create_revision():
            paiement.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
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
        with transaction.atomic(), reversion.create_revision():
            paiement.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in paiement.changed_data))
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
                with transaction.atomic(), reversion.create_revision():
                    paiement_del.delete()
                    reversion.set_user(request.user)
                    reversion.set_comment("Destruction")
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
        with transaction.atomic(), reversion.create_revision():
            banque.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "La banque a été ajoutée")
        return redirect("/cotisations/index_banque/")
    return form({'factureform': banque}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def edit_banque(request, banqueid):
    try:
        banque_instance = Banque.objects.get(pk=banqueid)
    except Banque.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/cotisations/index_banque/")
    banque = BanqueForm(request.POST or None, instance=banque_instance)
    if banque.is_valid():
        with transaction.atomic(), reversion.create_revision():
            banque.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in banque.changed_data))
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
                with transaction.atomic(), reversion.create_revision():
                    banque_del.delete()
                    reversion.set_user(request.user)
                    reversion.set_comment("Destruction")
                messages.success(request, "La banque a été supprimée")
            except ProtectedError:
                messages.error(request, "La banque %s est affectée à au moins une facture, vous ne pouvez pas la supprimer" % banque_del)
        return redirect("/cotisations/index_banque/")
    return form({'factureform': banque}, 'cotisations/facture.html', request)

@login_required
@permission_required('trésorier')
def control(request):
    options, created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    facture_list = Facture.objects.order_by('date').reverse()
    controlform_set = modelformset_factory(Facture, fields=('control','valid'), extra=0)
    paginator = Paginator(facture_list, pagination_number)
    page = request.GET.get('page')
    try:
        facture_list = paginator.page(page)
    except PageNotAnInteger:
        facture_list = paginator.page(1)
    except EmptyPage:
        facture_list = paginator.page(paginator.num.pages)
    page_query = Facture.objects.order_by('date').reverse().filter(id__in=[facture.id for facture in facture_list]) 
    controlform = controlform_set(request.POST or None, queryset=page_query)
    if controlform.is_valid():
        with transaction.atomic(), reversion.create_revision():
            controlform.save()
            reversion.set_user(request.user)
            reversion.set_comment("Controle trésorier")
        return redirect("/cotisations/control/")
    return render(request, 'cotisations/control.html', {'facture_list': facture_list, 'controlform': controlform})

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
    options, created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    facture_list = Facture.objects.order_by('date').select_related('user').select_related('paiement').prefetch_related('vente_set').reverse()
    paginator = Paginator(facture_list, pagination_number)
    page = request.GET.get('page')
    try:
        facture_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        facture_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        facture_list = paginator.page(paginator.num_pages)
    return render(request, 'cotisations/index.html', {'facture_list': facture_list})

@login_required
def history(request, object, id):
    if object == 'facture':
        try:
             object_instance = Facture.objects.get(pk=id)
        except Facture.DoesNotExist:
             messages.error(request, "Facture inexistante")
             return redirect("/cotisations/")
        if not request.user.has_perms(('cableur',)) and object_instance.user != request.user:
             messages.error(request, "Vous ne pouvez pas afficher l'historique d'une facture d'un autre user que vous sans droit cableur")
             return redirect("/users/profil/" + str(request.user.id))
    elif object == 'paiement' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Paiement.objects.get(pk=id)
        except Paiement.DoesNotExist:
             messages.error(request, "Paiement inexistant")
             return redirect("/cotisations/")
    elif object == 'article' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Article.objects.get(pk=id)
        except Article.DoesNotExist:
             messages.error(request, "Article inexistante")
             return redirect("/cotisations/")
    elif object == 'banque' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Banque.objects.get(pk=id)
        except Banque.DoesNotExist:
             messages.error(request, "Banque inexistante")
             return redirect("/cotisations/")
    else:
        messages.error(request, "Objet  inconnu")
        return redirect("/cotisations/")
    options, created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    reversions = Version.objects.get_for_object(object_instance)
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
    return render(request, 're2o/history.html', {'reversions': reversions, 'object': object_instance})
