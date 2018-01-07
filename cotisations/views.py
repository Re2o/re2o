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
from __future__ import unicode_literals
import os

from django.urls import reverse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import ProtectedError
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory, formset_factory
from django.utils import timezone
from reversion import revisions as reversion
from reversion.models import Version
# Import des models, forms et fonctions re2o
from users.models import User
from re2o.settings import LOGO_PATH
from re2o import settings
from re2o.views import form
from re2o.utils import SortTable
from re2o.acl import (
    can_create,
    can_edit,
    can_delete,
    can_view,
    can_view_all,
    can_delete_set,
    can_change,
)
from preferences.models import OptionalUser, AssoOption, GeneralOption
from .models import Facture, Article, Vente, Paiement, Banque
from .forms import (
    NewFactureForm,
    EditFactureForm,
    ArticleForm,
    DelArticleForm,
    PaiementForm,
    DelPaiementForm,
    BanqueForm,
    DelBanqueForm,
    NewFactureFormPdf,
    SelectUserArticleForm,
    SelectClubArticleForm,
    CreditSoldeForm
)
from .tex import render_invoice



@login_required
@can_create(Facture)
@can_edit(User)
def new_facture(request, user, userid):
    """Creation d'une facture pour un user. Renvoie la liste des articles
    et crée des factures dans un formset. Utilise un peu de js coté template
    pour ajouter des articles.
    Parse les article et boucle dans le formset puis save les ventes,
    enfin sauve la facture parente.
    TODO : simplifier cette fonction, déplacer l'intelligence coté models
    Facture et Vente."""
    facture = Facture(user=user)
    # Le template a besoin de connaitre les articles pour le js
    article_list = Article.objects.filter(
        Q(type_user='All') | Q(type_user=request.user.class_name)
    )
    # On envoie la form fature et un formset d'articles
    facture_form = NewFactureForm(request.POST or None, instance=facture)
    if request.user.is_class_club:
        article_formset = formset_factory(SelectClubArticleForm)(request.POST or None)
    else:
        article_formset = formset_factory(SelectUserArticleForm)(request.POST or None)
    if facture_form.is_valid() and article_formset.is_valid():
        new_facture_instance = facture_form.save(commit=False)
        articles = article_formset
        # Si au moins un article est rempli
        if any(art.cleaned_data for art in articles):
            options, _created = OptionalUser.objects.get_or_create()
            user_solde = options.user_solde
            solde_negatif = options.solde_negatif
            # Si on paye par solde, que l'option est activée,
            # on vérifie que le négatif n'est pas atteint
            if user_solde:
                if new_facture_instance.paiement == Paiement.objects.get_or_create(
                        moyen='solde'
                )[0]:
                    prix_total = 0
                    for art_item in articles:
                        if art_item.cleaned_data:
                            prix_total += art_item.cleaned_data['article']\
                                    .prix*art_item.cleaned_data['quantity']
                    if float(user.solde) - float(prix_total) < solde_negatif:
                        messages.error(request, "Le solde est insuffisant pour\
                                effectuer l'opération")
                        return redirect(reverse(
                            'users:profil',
                            kwargs={'userid': userid}
                            ))
            with transaction.atomic(), reversion.create_revision():
                new_facture_instance.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            for art_item in articles:
                if art_item.cleaned_data:
                    article = art_item.cleaned_data['article']
                    quantity = art_item.cleaned_data['quantity']
                    new_vente = Vente.objects.create(
                        facture=new_facture_instance,
                        name=article.name,
                        prix=article.prix,
                        type_cotisation=article.type_cotisation,
                        duration=article.duration,
                        number=quantity
                    )
                    with transaction.atomic(), reversion.create_revision():
                        new_vente.save()
                        reversion.set_user(request.user)
                        reversion.set_comment("Création")
            if any(art_item.cleaned_data['article'].type_cotisation
                   for art_item in articles if art_item.cleaned_data):
                messages.success(
                    request,
                    "La cotisation a été prolongée\
                    pour l'adhérent %s jusqu'au %s" % (
                        user.pseudo, user.end_adhesion()
                    )
                    )
            else:
                messages.success(request, "La facture a été crée")
            return redirect(reverse(
                'users:profil',
                kwargs={'userid': userid}
                ))
        messages.error(
            request,
            u"Il faut au moins un article valide pour créer une facture"
            )
    return form({
        'factureform': facture_form,
        'venteform': article_formset,
        'articlelist': article_list
        }, 'cotisations/new_facture.html', request)


@login_required
@can_change(Facture, 'pdf')
def new_facture_pdf(request):
    """Permet de générer un pdf d'une facture. Réservée
    au trésorier, permet d'emettre des factures sans objet
    Vente ou Facture correspondant en bdd"""
    facture_form = NewFactureFormPdf(request.POST or None)
    if facture_form.is_valid():
        options, _created = AssoOption.objects.get_or_create()
        tbl = []
        article = facture_form.cleaned_data['article']
        quantite = facture_form.cleaned_data['number']
        paid = facture_form.cleaned_data['paid']
        destinataire = facture_form.cleaned_data['dest']
        chambre = facture_form.cleaned_data['chambre']
        fid = facture_form.cleaned_data['fid']
        for art in article:
            tbl.append([art, quantite, art.prix * quantite])
        prix_total = sum(a[2] for a in tbl)
        user = {'name': destinataire, 'room': chambre}
        return render_invoice(request, {
            'DATE': timezone.now(),
            'dest': user,
            'fid': fid,
            'article': tbl,
            'total': prix_total,
            'paid': paid,
            'asso_name': options.name,
            'line1': options.adresse1,
            'line2': options.adresse2,
            'siret': options.siret,
            'email': options.contact,
            'phone': options.telephone,
            'tpl_path': os.path.join(settings.BASE_DIR, LOGO_PATH)
            })
    return form({
        'factureform': facture_form
        }, 'cotisations/facture.html', request)


@login_required
@can_view(Facture)
def facture_pdf(request, facture, factureid):
    """Affiche en pdf une facture. Cree une ligne par Vente de la facture,
    et génére une facture avec le total, le moyen de paiement, l'adresse
    de l'adhérent, etc. Réservée à self pour un user sans droits,
    les droits cableurs permettent d'afficher toute facture"""

    ventes_objects = Vente.objects.all().filter(facture=facture)
    ventes = []
    options, _created = AssoOption.objects.get_or_create()
    for vente in ventes_objects:
        ventes.append([vente, vente.number, vente.prix_total])
    return render_invoice(request, {
        'paid': True,
        'fid': facture.id,
        'DATE': facture.date,
        'dest': facture.user,
        'article': ventes,
        'total': facture.prix_total(),
        'asso_name': options.name,
        'line1': options.adresse1,
        'line2': options.adresse2,
        'siret': options.siret,
        'email': options.contact,
        'phone': options.telephone,
        'tpl_path': os.path.join(settings.BASE_DIR, LOGO_PATH)
        })


@login_required
@can_edit(Facture)
def edit_facture(request, facture, factureid):
    """Permet l'édition d'une facture. On peut y éditer les ventes
    déjà effectuer, ou rendre une facture invalide (non payées, chèque
    en bois etc). Mets à jour les durée de cotisation attenantes"""
    facture_form = EditFactureForm(request.POST or None, instance=facture, user=request.user)
    ventes_objects = Vente.objects.filter(facture=facture)
    vente_form_set = modelformset_factory(
        Vente,
        fields=('name', 'number'),
        extra=0,
        max_num=len(ventes_objects)
        )
    vente_form = vente_form_set(request.POST or None, queryset=ventes_objects)
    if facture_form.is_valid() and vente_form.is_valid():
        with transaction.atomic(), reversion.create_revision():
            facture_form.save()
            vente_form.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(
                field for form in vente_form for field
                in facture_form.changed_data + form.changed_data))
        messages.success(request, "La facture a bien été modifiée")
        return redirect(reverse('cotisations:index'))
    return form({
        'factureform': facture_form,
        'venteform': vente_form
        }, 'cotisations/edit_facture.html', request)


@login_required
@can_delete(Facture)
def del_facture(request, facture, factureid):
    """Suppression d'une facture. Supprime en cascade les ventes
    et cotisations filles"""
    if request.method == "POST":
        with transaction.atomic(), reversion.create_revision():
            facture.delete()
            reversion.set_user(request.user)
        messages.success(request, "La facture a été détruite")
        return redirect(reverse('cotisations:index'))
    return form({
        'objet': facture,
        'objet_name': 'facture'
        }, 'cotisations/delete.html', request)


@login_required
@can_create(Facture)
@can_edit(User)
def credit_solde(request, user, userid):
    """ Credit ou débit de solde """
    facture = CreditSoldeForm(request.POST or None)
    if facture.is_valid():
        facture_instance = facture.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            facture_instance.user = user
            facture_instance.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        new_vente = Vente.objects.create(
            facture=facture_instance,
            name="solde",
            prix=facture.cleaned_data['montant'],
            number=1
            )
        with transaction.atomic(), reversion.create_revision():
            new_vente.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Solde modifié")
        return redirect(reverse('cotisations:index'))
    return form({'factureform': facture}, 'cotisations/facture.html', request)


@login_required
@can_create(Article)
def add_article(request):
    """Ajoute un article. Champs : désignation,
    prix, est-ce une cotisation et si oui sa durée
    Réservé au trésorier
    Nota bene : les ventes déjà effectuées ne sont pas reliées
    aux articles en vente. La désignation, le prix... sont
    copiés à la création de la facture. Un changement de prix n'a
    PAS de conséquence sur les ventes déjà faites"""
    article = ArticleForm(request.POST or None)
    if article.is_valid():
        with transaction.atomic(), reversion.create_revision():
            article.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "L'article a été ajouté")
        return redirect(reverse('cotisations:index-article'))
    return form({'factureform': article}, 'cotisations/facture.html', request)


@login_required
@can_edit(Article)
def edit_article(request, article_instance, articleid):
    """Edition d'un article (designation, prix, etc)
    Réservé au trésorier"""
    article = ArticleForm(request.POST or None, instance=article_instance)
    if article.is_valid():
        with transaction.atomic(), reversion.create_revision():
            article.save()
            reversion.set_user(request.user)
            reversion.set_comment(
                "Champs modifié(s) : %s" % ', '.join(
                    field for field in article.changed_data
                )
            )
        messages.success(request, "Type d'article modifié")
        return redirect(reverse('cotisations:index-article'))
    return form({'factureform': article}, 'cotisations/facture.html', request)


@login_required
@can_delete_set(Article)
def del_article(request, instances):
    """Suppression d'un article en vente"""
    article = DelArticleForm(request.POST or None, instances=instances)
    if article.is_valid():
        article_del = article.cleaned_data['articles']
        with transaction.atomic(), reversion.create_revision():
            article_del.delete()
            reversion.set_user(request.user)
        messages.success(request, "Le/les articles ont été supprimé")
        return redirect(reverse('cotisations:index-article'))
    return form({'factureform': article}, 'cotisations/facture.html', request)


@login_required
@can_create(Paiement)
def add_paiement(request):
    """Ajoute un moyen de paiement. Relié aux factures
    via foreign key"""
    paiement = PaiementForm(request.POST or None)
    if paiement.is_valid():
        with transaction.atomic(), reversion.create_revision():
            paiement.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Le moyen de paiement a été ajouté")
        return redirect(reverse('cotisations:index-paiement'))
    return form({'factureform': paiement}, 'cotisations/facture.html', request)


@login_required
@can_edit(Paiement)
def edit_paiement(request, paiement_instance, paiementid):
    """Edition d'un moyen de paiement"""
    paiement = PaiementForm(request.POST or None, instance=paiement_instance)
    if paiement.is_valid():
        with transaction.atomic(), reversion.create_revision():
            paiement.save()
            reversion.set_user(request.user)
            reversion.set_comment(
                "Champs modifié(s) : %s" % ', '.join(
                    field for field in paiement.changed_data
                    )
            )
        messages.success(request, "Type de paiement modifié")
        return redirect(reverse('cotisations:index-paiement'))
    return form({'factureform': paiement}, 'cotisations/facture.html', request)


@login_required
@can_delete_set(Paiement)
def del_paiement(request, instances):
    """Suppression d'un moyen de paiement"""
    paiement = DelPaiementForm(request.POST or None, instances=instances)
    if paiement.is_valid():
        paiement_dels = paiement.cleaned_data['paiements']
        for paiement_del in paiement_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    paiement_del.delete()
                    reversion.set_user(request.user)
                    reversion.set_comment("Destruction")
                messages.success(
                    request,
                    "Le moyen de paiement a été supprimé"
                    )
            except ProtectedError:
                messages.error(
                    request,
                    "Le moyen de paiement %s est affecté à au moins une\
                    facture, vous ne pouvez pas le supprimer" % paiement_del
                )
        return redirect(reverse('cotisations:index-paiement'))
    return form({'factureform': paiement}, 'cotisations/facture.html', request)


@login_required
@can_create(Banque)
def add_banque(request):
    """Ajoute une banque à la liste des banques"""
    banque = BanqueForm(request.POST or None)
    if banque.is_valid():
        with transaction.atomic(), reversion.create_revision():
            banque.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "La banque a été ajoutée")
        return redirect(reverse('cotisations:index-banque'))
    return form({'factureform': banque}, 'cotisations/facture.html', request)


@login_required
@can_edit(Banque)
def edit_banque(request, banque_instance, banqueid):
    """Edite le nom d'une banque"""
    banque = BanqueForm(request.POST or None, instance=banque_instance)
    if banque.is_valid():
        with transaction.atomic(), reversion.create_revision():
            banque.save()
            reversion.set_user(request.user)
            reversion.set_comment(
                "Champs modifié(s) : %s" % ', '.join(
                    field for field in banque.changed_data
                )
            )
        messages.success(request, "Banque modifiée")
        return redirect(reverse('cotisations:index-banque'))
    return form({'factureform': banque}, 'cotisations/facture.html', request)


@login_required
@can_delete_set(Banque)
def del_banque(request, instances):
    """Supprime une banque"""
    banque = DelBanqueForm(request.POST or None, instances=instances)
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
                messages.error(request, "La banque %s est affectée à au moins\
                    une facture, vous ne pouvez pas la supprimer" % banque_del)
        return redirect(reverse('cotisations:index-banque'))
    return form({'factureform': banque}, 'cotisations/facture.html', request)


@login_required
@can_view_all(Facture)
@can_change(Facture, 'control')
def control(request):
    """Pour le trésorier, vue pour controler en masse les
    factures.Case à cocher, pratique"""
    options, _created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    facture_list = Facture.objects.select_related('user').select_related('paiement')
    facture_list = SortTable.sort(
        facture_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.COTISATIONS_CONTROL
    )
    controlform_set = modelformset_factory(
        Facture,
        fields=('control', 'valid'),
        extra=0
        )
    paginator = Paginator(facture_list, pagination_number)
    page = request.GET.get('page')
    try:
        facture_list = paginator.page(page)
    except PageNotAnInteger:
        facture_list = paginator.page(1)
    except EmptyPage:
        facture_list = paginator.page(paginator.num.pages)
    controlform = controlform_set(request.POST or None, queryset=facture_list.object_list)
    if controlform.is_valid():
        with transaction.atomic(), reversion.create_revision():
            controlform.save()
            reversion.set_user(request.user)
            reversion.set_comment("Controle trésorier")
        return redirect(reverse('cotisations:control'))
    return render(request, 'cotisations/control.html', {
        'facture_list': facture_list,
        'controlform': controlform
        })


@login_required
@can_view_all(Article)
def index_article(request):
    """Affiche l'ensemble des articles en vente"""
    article_list = Article.objects.order_by('name')
    return render(request, 'cotisations/index_article.html', {
        'article_list': article_list
        })


@login_required
@can_view_all(Paiement)
def index_paiement(request):
    """Affiche l'ensemble des moyens de paiement en vente"""
    paiement_list = Paiement.objects.order_by('moyen')
    return render(request, 'cotisations/index_paiement.html', {
        'paiement_list': paiement_list
        })


@login_required
@can_view_all(Banque)
def index_banque(request):
    """Affiche l'ensemble des banques"""
    banque_list = Banque.objects.order_by('name')
    return render(request, 'cotisations/index_banque.html', {
        'banque_list': banque_list
        })


@login_required
@can_view_all(Facture)
def index(request):
    """Affiche l'ensemble des factures, pour les cableurs et +"""
    options, _created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    facture_list = Facture.objects.select_related('user')\
        .select_related('paiement').prefetch_related('vente_set')
    facture_list = SortTable.sort(
        facture_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.COTISATIONS_INDEX
    )
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
    return render(request, 'cotisations/index.html', {
        'facture_list': facture_list
        })
