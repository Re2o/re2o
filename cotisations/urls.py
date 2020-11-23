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

from django.conf.urls import url

from . import views
from . import payment_methods

urlpatterns = [
    url(r"^new_facture/(?P<userid>[0-9]+)$", views.new_facture, name="new-facture"),
    url(
        r"^edit_facture/(?P<factureid>[0-9]+)$", views.edit_facture, name="edit-facture"
    ),
    url(r"^del_facture/(?P<factureid>[0-9]+)$", views.del_facture, name="del-facture"),
    url(r"^facture_pdf/(?P<factureid>[0-9]+)$", views.facture_pdf, name="facture-pdf"),
    url(r"^voucher_pdf/(?P<factureid>[0-9]+)$", views.voucher_pdf, name="voucher-pdf"),
    url(r"^new_cost_estimate/$", views.new_cost_estimate, name="new-cost-estimate"),
    url(
        r"^index_cost_estimate/$", views.index_cost_estimate, name="index-cost-estimate"
    ),
    url(
        r"^cost_estimate_pdf/(?P<costestimateid>[0-9]+)$",
        views.cost_estimate_pdf,
        name="cost-estimate-pdf",
    ),
    url(
        r"^index_custom_invoice/$",
        views.index_custom_invoice,
        name="index-custom-invoice",
    ),
    url(
        r"^edit_cost_estimate/(?P<costestimateid>[0-9]+)$",
        views.edit_cost_estimate,
        name="edit-cost-estimate",
    ),
    url(
        r"^cost_estimate_to_invoice/(?P<costestimateid>[0-9]+)$",
        views.cost_estimate_to_invoice,
        name="cost-estimate-to-invoice",
    ),
    url(
        r"^del_cost_estimate/(?P<costestimateid>[0-9]+)$",
        views.del_cost_estimate,
        name="del-cost-estimate",
    ),
    url(r"^new_custom_invoice/$", views.new_custom_invoice, name="new-custom-invoice"),
    url(
        r"^edit_custom_invoice/(?P<custominvoiceid>[0-9]+)$",
        views.edit_custom_invoice,
        name="edit-custom-invoice",
    ),
    url(
        r"^custom_invoice_pdf/(?P<custominvoiceid>[0-9]+)$",
        views.custom_invoice_pdf,
        name="custom-invoice-pdf",
    ),
    url(
        r"^del_custom_invoice/(?P<custominvoiceid>[0-9]+)$",
        views.del_custom_invoice,
        name="del-custom-invoice",
    ),
    url(r"^credit_solde/(?P<userid>[0-9]+)$", views.credit_solde, name="credit-solde"),
    url(r"^add_article/$", views.add_article, name="add-article"),
    url(
        r"^edit_article/(?P<articleid>[0-9]+)$", views.edit_article, name="edit-article"
    ),
    url(r"^del_article/$", views.del_article, name="del-article"),
    url(r"^add_paiement/$", views.add_paiement, name="add-paiement"),
    url(
        r"^edit_paiement/(?P<paiementid>[0-9]+)$",
        views.edit_paiement,
        name="edit-paiement",
    ),
    url(r"^del_paiement/$", views.del_paiement, name="del-paiement"),
    url(r"^add_banque/$", views.add_banque, name="add-banque"),
    url(r"^edit_banque/(?P<banqueid>[0-9]+)$", views.edit_banque, name="edit-banque"),
    url(r"^del_banque/$", views.del_banque, name="del-banque"),
    url(r"^index_article/$", views.index_article, name="index-article"),
    url(r"^index_banque/$", views.index_banque, name="index-banque"),
    url(r"^index_paiement/$", views.index_paiement, name="index-paiement"),
    url(r"^control/$", views.control, name="control"),
    url(r"^$", views.index, name="index"),
] + payment_methods.urls.urlpatterns
