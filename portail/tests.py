# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2021  Yohann D'ANELLO
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

from cotisations.models import Article, Paiement, Vente
from cotisations.payment_methods.comnpay.models import ComnpayPayment
from django.test import TestCase
from django.urls import reverse_lazy
from users.models import Adherent


class TestPortal(TestCase):
    def setUp(self) -> None:
        self.payment = Paiement.objects.create()
        self.comnpay_payment = ComnpayPayment.objects.create(payment=self.payment)
        self.article = Article.objects.create(
            available_for_everyone=True,
            duration_days_membership=365,
            duration_days_connection=365,
        )

    def test_index(self):
        resp = self.client.get(reverse_lazy("portail:index"))
        self.assertEqual(resp.status_code, 200)

    def test_create_account(self):
        resp = self.client.get(reverse_lazy("portail:signup"))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(reverse_lazy("portail:signup"), data=dict(
            name="Toto",
            surname="TOTO",
            pseudo="toto",
            email="toto@example.com",
            telephone="0123456789",
            password1="azertyuiopazertyuiop",
            password2="azertyuiopazertyuiop",
            room="",
            school="",
            former_user_check=True,
            gtu_check=True,
            payment_method=self.payment.pk,
            article=self.article.pk,
        ))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Adherent.objects.filter(pseudo="toto").exists())
        self.assertTrue(Vente.objects.filter(article=self.article).exists())

    def test_authenticated_user(self):
        adh = Adherent.objects.create()
        self.client.force_login(adh)

        resp = self.client.get(reverse_lazy("portail:index"))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse_lazy("portail:extend-connection", args=(adh.pk,)))
        self.assertEqual(resp.status_code, 200)
