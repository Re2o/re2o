from django.test import TestCase

import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from users.models import User
from .models import Vente, Facture, Cotisation, Paiement


class VenteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(pseudo="testUser", email="test@example.org")
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
        purchase = Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration=1,
            duration_days=0,
            type_cotisation="All",
            prix=0,
        )
        delta = relativedelta(self.user.end_connexion(), date)
        delta.microseconds = 0
        self.assertEqual(delta, relativedelta(months=1))

    def test_one_month_and_one_week_cotisation(self):
        """
        It should be possible to have one day membership.
        """
        date = timezone.now()
        purchase = Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration=1,
            duration_days=7,
            type_cotisation="All",
            prix=0,
        )
        delta = relativedelta(self.user.end_connexion(), date)
        delta.microseconds = 0
        self.assertEqual(delta, relativedelta(months=1, days=7))

    def tearDown(self):
        self.f.delete()
        self.user.delete()
        self.paiement.delete()
