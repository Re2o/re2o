# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
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
"""cotisations.urls
The defined URLs for the Cotisations app
"""

from __future__ import unicode_literals

from django.urls import path

from . import payment_methods, views, views_autocomplete

app_name = "cotisations"

urlpatterns = [
    path("new_facture/<int:userid>", views.new_facture, name="new-facture"),
    path("edit_facture/<int:factureid>", views.edit_facture, name="edit-facture"),
    path("del_facture/<int:factureid>", views.del_facture, name="del-facture"),
    path("facture_pdf/<int:factureid>", views.facture_pdf, name="facture-pdf"),
    path("voucher_pdf/<int:factureid>", views.voucher_pdf, name="voucher-pdf"),
    path("new_cost_estimate", views.new_cost_estimate, name="new-cost-estimate"),
    path("index_cost_estimate", views.index_cost_estimate, name="index-cost-estimate"),
    path(
        "cost_estimate_pdf/<int:costestimateid>",
        views.cost_estimate_pdf,
        name="cost-estimate-pdf",
    ),
    path(
        "index_custom_invoice",
        views.index_custom_invoice,
        name="index-custom-invoice",
    ),
    path(
        "edit_cost_estimate/<int:costestimateid>",
        views.edit_cost_estimate,
        name="edit-cost-estimate",
    ),
    path(
        "cost_estimate_to_invoice/<int:costestimateid>",
        views.cost_estimate_to_invoice,
        name="cost-estimate-to-invoice",
    ),
    path(
        "del_cost_estimate/<int:costestimateid>",
        views.del_cost_estimate,
        name="del-cost-estimate",
    ),
    path("new_custom_invoice", views.new_custom_invoice, name="new-custom-invoice"),
    path(
        "edit_custom_invoice/<int:custominvoiceid>",
        views.edit_custom_invoice,
        name="edit-custom-invoice",
    ),
    path(
        "custom_invoice_pdf/<int:custominvoiceid>",
        views.custom_invoice_pdf,
        name="custom-invoice-pdf",
    ),
    path(
        "del_custom_invoice/<int:custominvoiceid>",
        views.del_custom_invoice,
        name="del-custom-invoice",
    ),
    path("credit_solde/<int:userid>", views.credit_solde, name="credit-solde"),
    path("add_article", views.add_article, name="add-article"),
    path("edit_article/<int:articleid>", views.edit_article, name="edit-article"),
    path("del_article", views.del_article, name="del-article"),
    path("add_paiement", views.add_paiement, name="add-paiement"),
    path(
        "edit_paiement/<int:paiementid>",
        views.edit_paiement,
        name="edit-paiement",
    ),
    path("del_paiement", views.del_paiement, name="del-paiement"),
    path("add_banque", views.add_banque, name="add-banque"),
    path("edit_banque/<int:banqueid>", views.edit_banque, name="edit-banque"),
    path("del_banque", views.del_banque, name="del-banque"),
    path("index_article", views.index_article, name="index-article"),
    path("index_banque", views.index_banque, name="index-banque"),
    path("index_paiement", views.index_paiement, name="index-paiement"),
    path("control", views.control, name="control"),
    path("", views.index, name="index"),
    ### Autocomplete Views
    path(
        "banque-autocomplete",
        views_autocomplete.BanqueAutocomplete.as_view(),
        name="banque-autocomplete",
    ),
] + payment_methods.urls.urlpatterns
