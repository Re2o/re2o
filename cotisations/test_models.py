from django.test import TestCase

import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from users.models import User
from .models import Vente, Facture, Cotisation, Paiement


class VenteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(pseudo="testUserPlop", email="test@example.org")
        self.paiement = Paiement.objects.create(moyen="test payment")
        self.f = Facture.objects.create(
            user=self.user, paiement=self.paiement, valid=True
        )

    def test_one_day_cotisation(self):
        """
        It should be possible to have one day membership.
        """
        date = timezone.now()
        purchase = Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration=0,
            duration_days=1,
            type_cotisation="All",
            prix=0,
        )
        self.f.reorder_purchases()
        self.assertAlmostEqual(
            self.user.end_connexion() - date,
            datetime.timedelta(days=1),
            delta=datetime.timedelta(seconds=1),
        )

    def test_one_month_cotisation(self):
        """
        It should be possible to have one day membership.
        """
        date = timezone.now()
        Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration=1,
            duration_days=0,
            type_cotisation="All",
            prix=0,
        )
        self.f.reorder_purchases()
        end = self.user.end_connexion()
        expected_end = date + relativedelta(months=1)
        self.assertEqual(end.day, expected_end.day)
        self.assertEqual(end.month, expected_end.month)
        self.assertEqual(end.year, expected_end.year)

    def test_one_month_and_one_week_cotisation(self):
        """
        It should be possible to have one day membership.
        """
        date = timezone.now()
        Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration=1,
            duration_days=7,
            type_cotisation="All",
            prix=0,
        )
        self.f.reorder_purchases()
        end = self.user.end_connexion()
        expected_end = date + relativedelta(months=1, days=7)
        self.assertEqual(end.day, expected_end.day)
        self.assertEqual(end.month, expected_end.month)
        self.assertEqual(end.year, expected_end.year)

    def tearDown(self):
        self.f.delete()
        self.user.delete()
        self.paiement.delete()


class FactureModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(pseudo="testUserPlop", email="test@example.org")
        self.paiement = Paiement.objects.create(moyen="test payment")
    def tearDown(self):
        self.user.delete()
        self.paiement.delete()
    def test_cotisations_prolongation(self):
        """When user already have one valid cotisation, the new one should be
        added at the end of the existing one."""
        date = timezone.now()
        invoice1 = Facture.objects.create(
            user=self.user, paiement=self.paiement, valid=True
        )
        Vente.objects.create(
            facture=invoice1,
            number=1,
            name="Test purchase",
            duration=1,
            duration_days=0,
            type_cotisation="All",
            prix=0,
        )
        invoice1.reorder_purchases()
        invoice2 = Facture.objects.create(
            user=self.user, paiement=self.paiement, valid=True
        )
        Vente.objects.create(
            facture=invoice2,
            number=1,
            name="Test purchase",
            duration=1,
            duration_days=0,
            type_cotisation="All",
            prix=0,
        )
        invoice1.reorder_purchases()
        delta = relativedelta(self.user.end_connexion(), date)
        delta.microseconds = 0
        try:
            self.assertEqual(delta, relativedelta(months=2))
        except Exception as e:
            invoice1.delete()
            invoice2.delete()
            raise e
        invoice1.delete()
        invoice2.delete()

