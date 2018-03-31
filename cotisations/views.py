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
from django.core.validators import MaxValueValidator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import ProtectedError
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory, formset_factory
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_variables
# Import des models, forms et fonctions re2o
from reversion import revisions as reversion
from users.models import User
from re2o.settings import LOGO_PATH
from re2o import settings
from re2o.views import form
from re2o.utils import SortTable, re2o_paginator
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
    CreditSoldeForm,
    NewFactureSoldeForm,
    RechargeForm
)
from . import payment
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
    # TODO : translate docstring to English
    # TODO : change facture to invoice
    facture = Facture(user=user)
    # TODO : change comment to English
    # Le template a besoin de connaitre les articles pour le js
    article_list = Article.objects.filter(
        Q(type_user='All') | Q(type_user=request.user.class_name)
    )
    # On envoie la form fature et un formset d'articles
    # TODO : change facture to invoice
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
            # TODO : change solde to balance
            user_solde = OptionalUser.get_cached_value('user_solde')
            solde_negatif = OptionalUser.get_cached_value('solde_negatif')
            # Si on paye par solde, que l'option est activée,
            # on vérifie que le négatif n'est pas atteint
            if user_solde:
                # TODO : change Paiement to Payment
                if new_facture_instance.paiement == Paiement.objects.get_or_create(
                        moyen='solde'
                )[0]:
                    prix_total = 0
                    for art_item in articles:
                        if art_item.cleaned_data:
                            # change prix to price
                            prix_total += art_item.cleaned_data['article']\
                                    .prix*art_item.cleaned_data['quantity']
                    if float(user.solde) - float(prix_total) < solde_negatif:
                        messages.error(
                            request,
                            _("Your balance is too low for this operation.")
                        )
                        return redirect(reverse(
                            'users:profil',
                            kwargs={'userid': userid}
                        ))
            new_facture_instance.save()
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
                    new_vente.save()
            if any(art_item.cleaned_data['article'].type_cotisation
                   for art_item in articles if art_item.cleaned_data):
                messages.success(
                    request,
                    _("The cotisation of %(member_name)s has been \
                    extended to %(end_date)s.") % {
                        member_name: user.pseudo,
                        end_date: user.end_adhesion()
                    }
                )
            else:
                messages.success(
                    request,
                    _("The invoice has been created.")
                )
            return redirect(reverse(
                'users:profil',
                kwargs={'userid': userid}
            ))
        messages.error(
            request,
            _("You need to choose at least one article.")
        )
    return form(
        {
            'factureform': facture_form,
            'venteform': article_formset,
            'articlelist': article_list
        },
        'cotisations/new_facture.html', request
    )


# TODO : change facture to invoice
@login_required
@can_change(Facture, 'pdf')
def new_facture_pdf(request):
    """Permet de générer un pdf d'une facture. Réservée
    au trésorier, permet d'emettre des factures sans objet
    Vente ou Facture correspondant en bdd"""
    # TODO : translate docstring to English
    facture_form = NewFactureFormPdf(request.POST or None)
    if facture_form.is_valid():
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
            'asso_name': AssoOption.get_cached_value('name'),
            'line1': AssoOption.get_cached_value('adresse1'),
            'line2': AssoOption.get_cached_value('adresse2'),
            'siret': AssoOption.get_cached_value('siret'),
            'email': AssoOption.get_cached_value('contact'),
            'phone': AssoOption.get_cached_value('telephone'),
            'tpl_path': os.path.join(settings.BASE_DIR, LOGO_PATH)
            })
    return form({
        'factureform': facture_form,
        'action_name' : 'Editer'
        }, 'cotisations/facture.html', request)


# TODO : change facture to invoice
@login_required
@can_view(Facture)
def facture_pdf(request, facture, factureid):
    """Affiche en pdf une facture. Cree une ligne par Vente de la facture,
    et génére une facture avec le total, le moyen de paiement, l'adresse
    de l'adhérent, etc. Réservée à self pour un user sans droits,
    les droits cableurs permettent d'afficher toute facture"""
    # TODO : translate docstring to English
    # TODO : change vente to purchase
    ventes_objects = Vente.objects.all().filter(facture=facture)
    ventes = []
    for vente in ventes_objects:
        ventes.append([vente, vente.number, vente.prix_total])
    return render_invoice(request, {
        'paid': True,
        'fid': facture.id,
        'DATE': facture.date,
        'dest': facture.user,
        'article': ventes,
        'total': facture.prix_total(),
        'asso_name': AssoOption.get_cached_value('name'),
        'line1': AssoOption.get_cached_value('adresse1'),
        'line2': AssoOption.get_cached_value('adresse2'),
        'siret': AssoOption.get_cached_value('siret'),
        'email': AssoOption.get_cached_value('contact'),
        'phone': AssoOption.get_cached_value('telephone'),
        'tpl_path': os.path.join(settings.BASE_DIR, LOGO_PATH)
        })


# TODO : change facture to invoice
@login_required
@can_edit(Facture)
def edit_facture(request, facture, factureid):
    """Permet l'édition d'une facture. On peut y éditer les ventes
    déjà effectuer, ou rendre une facture invalide (non payées, chèque
    en bois etc). Mets à jour les durée de cotisation attenantes"""
    # TODO : translate docstring to English
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
        if facture_form.changed_data:
            facture_form.save()
        vente_form.save()
        messages.success(
            request,
            _("The invoice has been successfully edited.")
        )
        return redirect(reverse('cotisations:index'))
    return form({
        'factureform': facture_form,
        'venteform': vente_form
        }, 'cotisations/edit_facture.html', request)


# TODO : change facture to invoice
@login_required
@can_delete(Facture)
def del_facture(request, facture, factureid):
    """Suppression d'une facture. Supprime en cascade les ventes
    et cotisations filles"""
    # TODO : translate docstring to English
    if request.method == "POST":
        messages.success(
            request,
            _("The invoice has been successfully deleted")
        )
        return redirect(reverse('cotisations:index'))
    return form({
        'objet': facture,
        'objet_name': 'facture'
        }, 'cotisations/delete.html', request)


# TODO : change solde to balance
@login_required
@can_create(Facture)
@can_edit(User)
def credit_solde(request, user, userid):
    """ Credit ou débit de solde """
    # TODO : translate docstring to English
    # TODO : change facture to invoice
    facture = CreditSoldeForm(request.POST or None)
    if facture.is_valid():
        facture_instance = facture.save(commit=False)
        facture_instance.user = user
        facture_instance.save()
        new_vente = Vente.objects.create(
            facture=facture_instance,
            name="solde",
            prix=facture.cleaned_data['montant'],
            number=1
            )
        new_vente.save()
        messages.success(
            request,
            _("Banlance successfully updated.")
        )
        return redirect(reverse('cotisations:index'))
    return form({'factureform': facture, 'action_name' : 'Créditer'}, 'cotisations/facture.html', request)


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
    # TODO : translate docstring to English
    article = ArticleForm(request.POST or None)
    if article.is_valid():
        article.save()
        messages.success(
            request,
            _("The article has been successfully created.")
        )
        return redirect(reverse('cotisations:index-article'))
    return form({'factureform': article, 'action_name' : 'Ajouter'}, 'cotisations/facture.html', request)


@login_required
@can_edit(Article)
def edit_article(request, article_instance, articleid):
    """Edition d'un article (designation, prix, etc)
    Réservé au trésorier"""
    # TODO : translate dosctring to English
    article = ArticleForm(request.POST or None, instance=article_instance)
    if article.is_valid():
        if article.changed_data:
            article.save()
            messages.success(
                request,
                _("The article has been successfully edited.")
            )
        return redirect(reverse('cotisations:index-article'))
    return form({'factureform': article, 'action_name' : 'Editer'}, 'cotisations/facture.html', request)


@login_required
@can_delete_set(Article)
def del_article(request, instances):
    """Suppression d'un article en vente"""
    # TODO : translate docstring to English
    article = DelArticleForm(request.POST or None, instances=instances)
    if article.is_valid():
        article_del = article.cleaned_data['articles']
        article_del.delete()
        messages.success(
            request,
            _("The article(s) have been successfully deleted.")
        )
        return redirect(reverse('cotisations:index-article'))
    return form({'factureform': article, 'action_name' : 'Supprimer'}, 'cotisations/facture.html', request)


# TODO : change paiement to payment
@login_required
@can_create(Paiement)
def add_paiement(request):
    """Ajoute un moyen de paiement. Relié aux factures
    via foreign key"""
    # TODO : translate docstring to English
    # TODO : change paiement to Payment
    paiement = PaiementForm(request.POST or None)
    if paiement.is_valid():
        paiement.save()
        messages.success(
            request,
            _("The payment method has been successfully created.")
        )
        return redirect(reverse('cotisations:index-paiement'))
    return form({'factureform': paiement, 'action_name' : 'Ajouter'}, 'cotisations/facture.html', request)


# TODO : chnage paiement to Payment
@login_required
@can_edit(Paiement)
def edit_paiement(request, paiement_instance, paiementid):
    """Edition d'un moyen de paiement"""
    # TODO : translate docstring to English
    paiement = PaiementForm(request.POST or None, instance=paiement_instance)
    if paiement.is_valid():
        if paiement.changed_data:
            paiement.save()
            messages.success(
                request,
                _("The payement method has been successfully edited.")
            )
        return redirect(reverse('cotisations:index-paiement'))
    return form({'factureform': paiement, 'action_name' : 'Editer'}, 'cotisations/facture.html', request)


# TODO : change paiement to payment
@login_required
@can_delete_set(Paiement)
def del_paiement(request, instances):
    """Suppression d'un moyen de paiement"""
    # TODO : translate docstring to English
    paiement = DelPaiementForm(request.POST or None, instances=instances)
    if paiement.is_valid():
        paiement_dels = paiement.cleaned_data['paiements']
        for paiement_del in paiement_dels:
            try:
                paiement_del.delete()
                messages.success(
                    request,
                    _("The payment method %(method_name)s has been \
                    successfully deleted") % {
                        method_name: paiement_del
                    }
                )
            except ProtectedError:
                messages.error(
                    request,
                    _("The payment method %(method_name) can't be deleted \
                    because there are invoices using it.") % {
                        method_name: paiement_del
                    }
                )
        return redirect(reverse('cotisations:index-paiement'))
    return form({'factureform': paiement, 'action_name' : 'Supprimer'}, 'cotisations/facture.html', request)


# TODO : change banque to bank
@login_required
@can_create(Banque)
def add_banque(request):
    """Ajoute une banque à la liste des banques"""
    # TODO : tranlate docstring to English
    banque = BanqueForm(request.POST or None)
    if banque.is_valid():
        banque.save()
        messages.success(
            request,
            _("The bank has been successfully created.")
        )
        return redirect(reverse('cotisations:index-banque'))
    return form({'factureform': banque, 'action_name' : 'Ajouter'}, 'cotisations/facture.html', request)


# TODO : change banque to bank
@login_required
@can_edit(Banque)
def edit_banque(request, banque_instance, banqueid):
    """Edite le nom d'une banque"""
    # TODO : translate docstring to English
    banque = BanqueForm(request.POST or None, instance=banque_instance)
    if banque.is_valid():
        if banque.changed_data:
            banque.save()
            messages.success(
                request,
                _("The bank has been successfully edited")
            )
        return redirect(reverse('cotisations:index-banque'))
    return form({'factureform': banque, 'action_name' : 'Editer'}, 'cotisations/facture.html', request)


# TODO : chnage banque to bank
@login_required
@can_delete_set(Banque)
def del_banque(request, instances):
    """Supprime une banque"""
    # TODO : translate docstring to English
    banque = DelBanqueForm(request.POST or None, instances=instances)
    if banque.is_valid():
        banque_dels = banque.cleaned_data['banques']
        for banque_del in banque_dels:
            try:
                banque_del.delete()
                messages.success(
                    request,
                    _("The bank %(bank_name)s has been successfully \
                    deleted.") % {
                        bank_name: banque_del
                    }
                )
            except ProtectedError:
                messages.error(
                    request,
                    _("The bank %(bank_name)s can't be deleted \
                    because there are invoices using it.") % {
                        bank_name: banque_del
                    }
                )
        return redirect(reverse('cotisations:index-banque'))
    return form({'factureform': banque, 'action_name' : 'Supprimer'}, 'cotisations/facture.html', request)


# TODO : change facture to invoice
@login_required
@can_view_all(Facture)
@can_change(Facture, 'control')
def control(request):
    """Pour le trésorier, vue pour controler en masse les
    factures.Case à cocher, pratique"""
    # TODO : translate docstring to English
    pagination_number = GeneralOption.get_cached_value('pagination_number')
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
    facture_list = re2o_paginator(request, facture_list, pagination_number)
    controlform = controlform_set(request.POST or None, queryset=facture_list.object_list)
    if controlform.is_valid():
        controlform.save()
        reversion.set_comment("Controle")
        return redirect(reverse('cotisations:control'))
    return render(request, 'cotisations/control.html', {
        'facture_list': facture_list,
        'controlform': controlform
        })


@login_required
@can_view_all(Article)
def index_article(request):
    """Affiche l'ensemble des articles en vente"""
    # TODO : translate docstrign to English
    article_list = Article.objects.order_by('name')
    return render(request, 'cotisations/index_article.html', {
        'article_list': article_list
        })


# TODO : change paiement to payment
@login_required
@can_view_all(Paiement)
def index_paiement(request):
    """Affiche l'ensemble des moyens de paiement en vente"""
    # TODO : translate docstring to English
    paiement_list = Paiement.objects.order_by('moyen')
    return render(request, 'cotisations/index_paiement.html', {
        'paiement_list': paiement_list
        })


# TODO : change banque to bank
@login_required
@can_view_all(Banque)
def index_banque(request):
    """Affiche l'ensemble des banques"""
    # TODO : translate docstring to English
    banque_list = Banque.objects.order_by('name')
    return render(request, 'cotisations/index_banque.html', {
        'banque_list': banque_list
        })


@login_required
@can_view_all(Facture)
def index(request):
    """Affiche l'ensemble des factures, pour les cableurs et +"""
    # TODO : translate docstring to English
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    facture_list = Facture.objects.select_related('user')\
        .select_related('paiement').prefetch_related('vente_set')
    facture_list = SortTable.sort(
        facture_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.COTISATIONS_INDEX
    )
    facture_list = re2o_paginator(request, facture_list, pagination_number)
    return render(request, 'cotisations/index.html', {
        'facture_list': facture_list
        })


# TODO : change facture to invoice
@login_required
def new_facture_solde(request, userid):
    """Creation d'une facture pour un user. Renvoie la liste des articles
    et crée des factures dans un formset. Utilise un peu de js coté template
    pour ajouter des articles.
    Parse les article et boucle dans le formset puis save les ventes,
    enfin sauve la facture parente.
    TODO : simplifier cette fonction, déplacer l'intelligence coté models
    Facture et Vente."""
    # TODO : translate docstring to English
    user = request.user
    facture = Facture(user=user)
    paiement, _created = Paiement.objects.get_or_create(moyen='Solde')
    facture.paiement = paiement
    # TODO : translate comments to English
    # Le template a besoin de connaitre les articles pour le js
    article_list = Article.objects.filter(
        Q(type_user='All') | Q(type_user=request.user.class_name)
    )
    if request.user.is_class_club:
        article_formset = formset_factory(SelectClubArticleForm)(request.POST or None)
    else:
        article_formset = formset_factory(SelectUserArticleForm)(request.POST or None)
    if article_formset.is_valid():
        articles = article_formset
        # Si au moins un article est rempli
        if any(art.cleaned_data for art in articles):
            user_solde = OptionalUser.get_cached_value('user_solde')
            solde_negatif = OptionalUser.get_cached_value('solde_negatif')
            # Si on paye par solde, que l'option est activée,
            # on vérifie que le négatif n'est pas atteint
            if user_solde:
                prix_total = 0
                for art_item in articles:
                    if art_item.cleaned_data:
                        prix_total += art_item.cleaned_data['article']\
                                .prix*art_item.cleaned_data['quantity']
                if float(user.solde) - float(prix_total) < solde_negatif:
                    messages.error(
                        request,
                        _("The balance is too low for this operation.")
                    )
                    return redirect(reverse(
                        'users:profil',
                        kwargs={'userid': userid}
                    ))
            facture.save()
            for art_item in articles:
                if art_item.cleaned_data:
                    article = art_item.cleaned_data['article']
                    quantity = art_item.cleaned_data['quantity']
                    new_vente = Vente.objects.create(
                        facture=facture,
                        name=article.name,
                        prix=article.prix,
                        type_cotisation=article.type_cotisation,
                        duration=article.duration,
                        number=quantity
                    )
                    new_vente.save()
            if any(art_item.cleaned_data['article'].type_cotisation
                   for art_item in articles if art_item.cleaned_data):
                messages.success(
                    request,
                    _("The balance of %(member_name)s has been successfully \
                    extended to %(end_date)s") % {
                        member_name: user.pseudo,
                        end_date: user.end_adhesion()
                    }
                )
            else:
                messages.success(
                    request,
                    _("The invoice has been successuflly created.")
                )
            return redirect(reverse(
                'users:profil',
                kwargs={'userid': userid}
            ))
        messages.error(
            request,
            _("You need to choose at least one article.")
        )
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': userid}
        ))

    return form({
        'venteform': article_formset,
        'articlelist': article_list
        }, 'cotisations/new_facture_solde.html', request)


# TODO : change recharge to reload
@login_required
def recharge(request):
    if AssoOption.get_cached_value('payment') == 'NONE':
        messages.error(
            request,
            _("Online payment is disabled.")
        )
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': request.user.id}
        ))
    f = RechargeForm(request.POST or None, user=request.user)
    if f.is_valid():
        facture = Facture(user=request.user)
        paiement, _created = Paiement.objects.get_or_create(moyen='Rechargement en ligne')
        facture.paiement = paiement
        facture.valid = False
        facture.save()
        v = Vente.objects.create(
            facture=facture,
            name='solde',
            prix=f.cleaned_data['value'],
            number=1,
        )
        v.save()
        content = payment.PAYMENT_SYSTEM[AssoOption.get_cached_value('payment')](facture, request)
        return render(request, 'cotisations/payment.html', content)
    return form({'rechargeform':f}, 'cotisations/recharge.html', request)
