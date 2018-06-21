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
"""cotisations.urls
The defined URLs for the Cotisations app
"""

from __future__ import unicode_literals

from django.conf.urls import url

import re2o
from . import views
from . import payment_methods

urlpatterns = [
    url(
        r'^new_facture/(?P<userid>[0-9]+)$',
        views.new_facture,
        name='new-facture'
    ),
    url(
        r'^edit_facture/(?P<factureid>[0-9]+)$',
        views.edit_facture,
        name='edit-facture'
    ),
    url(
        r'^del_facture/(?P<factureid>[0-9]+)$',
        views.del_facture,
        name='del-facture'
    ),
    url(
        r'^facture_pdf/(?P<factureid>[0-9]+)$',
        views.facture_pdf,
        name='facture-pdf'
    ),
    url(
        r'^new_facture_pdf/$',
        views.new_facture_pdf,
        name='new-facture-pdf'
    ),
    url(
        r'^credit_solde/(?P<userid>[0-9]+)$',
        views.credit_solde,
        name='credit-solde'
    ),
    url(
        r'^add_article/$',
        views.add_article,
        name='add-article'
    ),
    url(
        r'^edit_article/(?P<articleid>[0-9]+)$',
        views.edit_article,
        name='edit-article'
    ),
    url(
        r'^del_article/$',
        views.del_article,
        name='del-article'
    ),
    url(
        r'^add_paiement/$',
        views.add_paiement,
        name='add-paiement'
    ),
    url(
        r'^edit_paiement/(?P<paiementid>[0-9]+)$',
        views.edit_paiement,
        name='edit-paiement'
    ),
    url(
        r'^del_paiement/$',
        views.del_paiement,
        name='del-paiement'
    ),
    url(
        r'^add_banque/$',
        views.add_banque,
        name='add-banque'
    ),
    url(
        r'^edit_banque/(?P<banqueid>[0-9]+)$',
        views.edit_banque,
        name='edit-banque'
    ),
    url(
        r'^del_banque/$',
        views.del_banque,
        name='del-banque'
    ),
    url(
        r'^index_article/$',
        views.index_article,
        name='index-article'
    ),
    url(
        r'^index_banque/$',
        views.index_banque,
        name='index-banque'
    ),
    url(
        r'^index_paiement/$',
        views.index_paiement,
        name='index-paiement'
    ),
    url(
        r'history/(?P<object_name>\w+)/(?P<object_id>[0-9]+)$',
        re2o.views.history,
        name='history',
        kwargs={'application': 'cotisations'},
    ),
    url(
        r'^control/$',
        views.control,
        name='control'
    ),
    url(
        r'^new_facture_solde/(?P<userid>[0-9]+)$',
        views.new_facture_solde,
        name='new_facture_solde'
    ),
    url(
        r'^recharge/$',
        views.recharge,
        name='recharge'
    ),
    url(r'^$', views.index, name='index'),
] + payment_methods.urlpatterns

