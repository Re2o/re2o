# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2018  Hugo Levy-Falk
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
"""cotisations.views
The different views used in the Cotisations module
"""

from __future__ import unicode_literals
import os

from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import ProtectedError
from django.db.models import Q
from django.forms import modelformset_factory, formset_factory
from django.utils import timezone
from django.utils.translation import ugettext as _

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
from preferences.models import AssoOption, GeneralOption
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
    RechargeForm
)
from .tex import render_invoice
from .payment_methods.forms import payment_method_factory


@login_required
@can_create(Facture)
@can_edit(User)
def new_facture(request, user, userid):
    """
    View called to create a new invoice.
    Currently, Send the list of available articles for the user along with
    a formset of a new invoice (based on the `:forms:NewFactureForm()` form.
    A bit of JS is used in the template to add articles in a fancier way.
    If everything is correct, save each one of the articles, save the
    purchase object associated and finally the newly created invoice.
    """
    invoice = Facture(user=user)
    # The template needs the list of articles (for the JS part)
    article_list = Article.objects.filter(
        Q(type_user='All') | Q(type_user=request.user.class_name)
    )
    # Building the invoice form and the article formset
    invoice_form = NewFactureForm(
        request.POST or None,
        instance=invoice,
        user=request.user
    )

    if request.user.is_class_club:
        article_formset = formset_factory(SelectClubArticleForm)(
            request.POST or None,
            form_kwargs={'user': request.user}
        )
    else:
        article_formset = formset_factory(SelectUserArticleForm)(
            request.POST or None,
            form_kwargs={'user': request.user}
        )

    if invoice_form.is_valid() and article_formset.is_valid():
        new_invoice_instance = invoice_form.save(commit=False)
        articles = article_formset
        # Check if at leat one article has been selected
        if any(art.cleaned_data for art in articles):
            new_invoice_instance.save()

            # Building a purchase for each article sold
            for art_item in articles:
                if art_item.cleaned_data:
                    article = art_item.cleaned_data['article']
                    quantity = art_item.cleaned_data['quantity']
                    new_purchase = Vente.objects.create(
                        facture=new_invoice_instance,
                        name=article.name,
                        prix=article.prix,
                        type_cotisation=article.type_cotisation,
                        duration=article.duration,
                        number=quantity
                    )
                    new_purchase.save()

            return new_invoice_instance.paiement.end_payment(
                new_invoice_instance,
                request
            )

        messages.error(
            request,
            _("You need to choose at least one article.")
        )
    return form(
        {
            'factureform': invoice_form,
            'venteform': article_formset,
            'articlelist': article_list
        },
        'cotisations/new_facture.html', request
    )


# TODO : change facture to invoice
@login_required
@can_change(Facture, 'pdf')
def new_facture_pdf(request):
    """
    View used to generate a custom PDF invoice. It's mainly used to
    get invoices that are not taken into account, for the administrative
    point of view.
    """
    # The template needs the list of articles (for the JS part)
    articles = Article.objects.filter(
        Q(type_user='All') | Q(type_user=request.user.class_name)
    )
    # Building the invocie form and the article formset
    invoice_form = NewFactureFormPdf(request.POST or None)
    if request.user.is_class_club:
        articles_formset = formset_factory(SelectClubArticleForm)(
            request.POST or None
        )
    else:
        articles_formset = formset_factory(SelectUserArticleForm)(
            request.POST or None
        )
    if invoice_form.is_valid() and articles_formset.is_valid():
        # Get the article list and build an list out of it
        # contiaining (article_name, article_price, quantity, total_price)
        articles_info = []
        for articles_form in articles_formset:
            if articles_form.cleaned_data:
                article = articles_form.cleaned_data['article']
                quantity = articles_form.cleaned_data['quantity']
                articles_info.append({
                    'name': article.name,
                    'price': article.prix,
                    'quantity': quantity,
                    'total_price': article.prix * quantity
                })
        paid = invoice_form.cleaned_data['paid']
        recipient = invoice_form.cleaned_data['dest']
        address = invoice_form.cleaned_data['chambre']
        total_price = sum(a['total_price'] for a in articles_info)

        return render_invoice(request, {
            'DATE': timezone.now(),
            'recipient_name': recipient,
            'address': address,
            'article': articles_info,
            'total': total_price,
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
        'factureform': invoice_form,
        'action_name': _("Create"),
        'articlesformset': articles_formset,
        'articles': articles
    }, 'cotisations/facture.html', request)


# TODO : change facture to invoice
@login_required
@can_view(Facture)
def facture_pdf(request, facture, **_kwargs):
    """
    View used to generate a PDF file from  an existing invoice in database
    Creates a line for each Purchase (thus article sold) and generate the
    invoice with the total price, the payment method, the address and the
    legal information for the user.
    """
    # TODO : change vente to purchase
    purchases_objects = Vente.objects.all().filter(facture=facture)
    # Get the article list and build an list out of it
    # contiaining (article_name, article_price, quantity, total_price)
    purchases_info = []
    for purchase in purchases_objects:
        purchases_info.append({
            'name': purchase.name,
            'price': purchase.prix,
            'quantity': purchase.number,
            'total_price': purchase.prix_total
        })
    return render_invoice(request, {
        'paid': True,
        'fid': facture.id,
        'DATE': facture.date,
        'recipient_name': "{} {}".format(
            facture.user.name,
            facture.user.surname
        ),
        'address': facture.user.room,
        'article': purchases_info,
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
def edit_facture(request, facture, **_kwargs):
    """
    View used to edit an existing invoice.
    Articles can be added or remove to the invoice and quantity
    can be set as desired. This is also the view used to invalidate
    an invoice.
    """
    invoice_form = EditFactureForm(
        request.POST or None,
        instance=facture,
        user=request.user
    )
    purchases_objects = Vente.objects.filter(facture=facture)
    purchase_form_set = modelformset_factory(
        Vente,
        fields=('name', 'number'),
        extra=0,
        max_num=len(purchases_objects)
    )
    purchase_form = purchase_form_set(
        request.POST or None,
        queryset=purchases_objects
    )
    if invoice_form.is_valid() and purchase_form.is_valid():
        if invoice_form.changed_data:
            invoice_form.save()
        purchase_form.save()
        messages.success(
            request,
            _("The invoice has been successfully edited.")
        )
        return redirect(reverse('cotisations:index'))
    return form({
        'factureform': invoice_form,
        'venteform': purchase_form
    }, 'cotisations/edit_facture.html', request)


# TODO : change facture to invoice
@login_required
@can_delete(Facture)
def del_facture(request, facture, **_kwargs):
    """
    View used to delete an existing invocie.
    """
    if request.method == "POST":
        facture.delete()
        messages.success(
            request,
            _("The invoice has been successfully deleted.")
        )
        return redirect(reverse('cotisations:index'))
    return form({
        'objet': facture,
        'objet_name': _("Invoice")
    }, 'cotisations/delete.html', request)


@login_required
@can_create(Article)
def add_article(request):
    """
    View used to add an article.

    .. note:: If a purchase has already been sold, the price are calculated
        once and for all. That means even if the price of an article is edited
        later, it won't change the invoice. That is really important to keep
        this behaviour in order not to modify all the past and already
        accepted invoices.
    """
    article = ArticleForm(request.POST or None)
    if article.is_valid():
        article.save()
        messages.success(
            request,
            _("The article has been successfully created.")
        )
        return redirect(reverse('cotisations:index-article'))
    return form({
        'factureform': article,
        'action_name': _("Add")
    }, 'cotisations/facture.html', request)


@login_required
@can_edit(Article)
def edit_article(request, article_instance, **_kwargs):
    """
    View used to edit an article.
    """
    article = ArticleForm(request.POST or None, instance=article_instance)
    if article.is_valid():
        if article.changed_data:
            article.save()
            messages.success(
                request,
                _("The article has been successfully edited.")
            )
        return redirect(reverse('cotisations:index-article'))
    return form({
        'factureform': article,
        'action_name': _('Edit')
    }, 'cotisations/facture.html', request)


@login_required
@can_delete_set(Article)
def del_article(request, instances):
    """
    View used to delete one of the articles.
    """
    article = DelArticleForm(request.POST or None, instances=instances)
    if article.is_valid():
        article_del = article.cleaned_data['articles']
        article_del.delete()
        messages.success(
            request,
            _("The article(s) have been successfully deleted.")
        )
        return redirect(reverse('cotisations:index-article'))
    return form({
        'factureform': article,
        'action_name': _("Delete")
    }, 'cotisations/facture.html', request)


# TODO : change paiement to payment
@login_required
@can_create(Paiement)
def add_paiement(request):
    """
    View used to add a payment method.
    """
    payment = PaiementForm(request.POST or None, prefix='payment')
    payment_method = payment_method_factory(
        payment.instance,
        request.POST or None,
        prefix='payment_method'
    )
    if payment.is_valid() and payment_method.is_valid():
        payment = payment.save()
        payment_method.save(payment)
        messages.success(
            request,
            _("The payment method has been successfully created.")
        )
        return redirect(reverse('cotisations:index-paiement'))
    return form({
        'factureform': payment,
        'payment_method': payment_method,
        'action_name': _("Add")
    }, 'cotisations/facture.html', request)


# TODO : chnage paiement to Payment
@login_required
@can_edit(Paiement)
def edit_paiement(request, paiement_instance, **_kwargs):
    """
    View used to edit a payment method.
    """
    payment = PaiementForm(
        request.POST or None,
        instance=paiement_instance,
        prefix="payment"
    )
    payment_method = payment_method_factory(
        paiement_instance,
        request.POST or None,
        prefix='payment_method',
        creation=False
    )

    if payment.is_valid() and payment_method.is_valid():
        payment.save()
        payment_method.save()
        messages.success(
            request,
            _("The payement method has been successfully edited.")
        )
        return redirect(reverse('cotisations:index-paiement'))
    return form({
        'factureform': payment,
        'payment_method': payment_method,
        'action_name': _("Edit")
    }, 'cotisations/facture.html', request)


# TODO : change paiement to payment
@login_required
@can_delete_set(Paiement)
def del_paiement(request, instances):
    """
    View used to delete a set of payment methods.
    """
    payment = DelPaiementForm(request.POST or None, instances=instances)
    if payment.is_valid():
        payment_dels = payment.cleaned_data['paiements']
        for payment_del in payment_dels:
            try:
                payment_del.delete()
                messages.success(
                    request,
                    _("The payment method %(method_name)s has been \
                    successfully deleted.") % {
                        'method_name': payment_del
                    }
                )
            except ProtectedError:
                messages.error(
                    request,
                    _("The payment method %(method_name)s can't be deleted \
                    because there are invoices using it.") % {
                        'method_name': payment_del
                    }
                )
        return redirect(reverse('cotisations:index-paiement'))
    return form({
        'factureform': payment,
        'action_name': _("Delete")
    }, 'cotisations/facture.html', request)


# TODO : change banque to bank
@login_required
@can_create(Banque)
def add_banque(request):
    """
    View used to add a bank.
    """
    bank = BanqueForm(request.POST or None)
    if bank.is_valid():
        bank.save()
        messages.success(
            request,
            _("The bank has been successfully created.")
        )
        return redirect(reverse('cotisations:index-banque'))
    return form({
        'factureform': bank,
        'action_name': _("Add")
    }, 'cotisations/facture.html', request)


# TODO : change banque to bank
@login_required
@can_edit(Banque)
def edit_banque(request, banque_instance, **_kwargs):
    """
    View used to edit a bank.
    """
    bank = BanqueForm(request.POST or None, instance=banque_instance)
    if bank.is_valid():
        if bank.changed_data:
            bank.save()
            messages.success(
                request,
                _("The bank has been successfully edited")
            )
        return redirect(reverse('cotisations:index-banque'))
    return form({
        'factureform': bank,
        'action_name': _("Edit")
    }, 'cotisations/facture.html', request)


# TODO : chnage banque to bank
@login_required
@can_delete_set(Banque)
def del_banque(request, instances):
    """
    View used to delete a set of banks.
    """
    bank = DelBanqueForm(request.POST or None, instances=instances)
    if bank.is_valid():
        bank_dels = bank.cleaned_data['banques']
        for bank_del in bank_dels:
            try:
                bank_del.delete()
                messages.success(
                    request,
                    _("The bank %(bank_name)s has been successfully \
                    deleted.") % {
                        'bank_name': bank_del
                    }
                )
            except ProtectedError:
                messages.error(
                    request,
                    _("The bank %(bank_name)s can't be deleted \
                    because there are invoices using it.") % {
                        'bank_name': bank_del
                    }
                )
        return redirect(reverse('cotisations:index-banque'))
    return form({
        'factureform': bank,
        'action_name': _("Delete")
    }, 'cotisations/facture.html', request)


# TODO : change facture to invoice
@login_required
@can_view_all(Facture)
@can_change(Facture, 'control')
def control(request):
    """
    View used to control the invoices all at once.
    """
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    invoice_list = (Facture.objects.select_related('user').
                    select_related('paiement'))
    invoice_list = SortTable.sort(
        invoice_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.COTISATIONS_CONTROL
    )
    control_invoices_formset = modelformset_factory(
        Facture,
        fields=('control', 'valid'),
        extra=0
    )
    invoice_list = re2o_paginator(request, invoice_list, pagination_number)
    control_invoices_form = control_invoices_formset(
        request.POST or None,
        queryset=invoice_list.object_list
    )
    if control_invoices_form.is_valid():
        control_invoices_form.save()
        reversion.set_comment("Controle")
        messages.success(
            request,
            _("Your changes have been properly taken into account.")
        )
        return redirect(reverse('cotisations:control'))
    return render(request, 'cotisations/control.html', {
        'facture_list': invoice_list,
        'controlform': control_invoices_form
    })


@login_required
@can_view_all(Article)
def index_article(request):
    """
    View used to display the list of all available articles.
    """
    # TODO : Offer other means of sorting
    article_list = Article.objects.order_by('name')
    return render(request, 'cotisations/index_article.html', {
        'article_list': article_list
    })


# TODO : change paiement to payment
@login_required
@can_view_all(Paiement)
def index_paiement(request):
    """
    View used to display the list of all available payment methods.
    """
    payment_list = Paiement.objects.order_by('moyen')
    return render(request, 'cotisations/index_paiement.html', {
        'paiement_list': payment_list
    })


# TODO : change banque to bank
@login_required
@can_view_all(Banque)
def index_banque(request):
    """
    View used to display the list of all available banks.
    """
    bank_list = Banque.objects.order_by('name')
    return render(request, 'cotisations/index_banque.html', {
        'banque_list': bank_list
    })


@login_required
@can_view_all(Facture)
def index(request):
    """
    View used to display the list of all exisitng invoices.
    """
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    invoice_list = Facture.objects.select_related('user')\
        .select_related('paiement').prefetch_related('vente_set')
    invoice_list = SortTable.sort(
        invoice_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.COTISATIONS_INDEX
    )
    invoice_list = re2o_paginator(request, invoice_list, pagination_number)
    return render(request, 'cotisations/index.html', {
        'facture_list': invoice_list
    })


# TODO : change solde to balance
@login_required
@can_create(Facture)
@can_edit(User)
def credit_solde(request, user, **_kwargs):
    """
    View used to edit the balance of a user.
    Can be use either to increase or decrease a user's balance.
    """
    refill_form = RechargeForm(request.POST or None, user=request.user)
    if refill_form.is_valid():
        invoice = Facture(user=request.user)
        invoice.paiement = refill_form.cleaned_data['payment']
        invoice.valid = False
        invoice.save()
        Vente.objects.create(
            facture=invoice,
            name='solde',
            prix=refill_form.cleaned_data['value'],
            number=1
        )
        return invoice.paiement.end_payment(invoice, request)
    return form({
        'factureform': refill_form,
        'balance': request.user.solde,
        'title': _("Refill your balance"),
        'action_name': _("Pay")
    }, 'cotisations/facture.html', request)
