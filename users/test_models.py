import datetime

from django.test import TestCase
from django.utils import timezone

from cotisations.models import Facture, Paiement, Vente
from users.models import User


class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(pseudo="testUser")

    def tearDown(self):
        self.user.facture_set.all().delete()
        self.user.delete()

    def test_multiple_cotisations_are_taken_into_account(self):
        paiement = Paiement.objects.create(moyen="test payment")
        invoice = Facture.objects.create(user=self.user, paiement=paiement, valid=True)
        date = timezone.now()
        purchase1 = Vente.objects.create(
            facture=invoice,
            number=1,
            name="Test purchase",
            duration=0,
            duration_days=1,
            type_cotisation="All",
            prix=0,
        )
        purchase2 = Vente.objects.create(
            facture=invoice,
            number=1,
            name="Test purchase",
            duration=0,
            duration_days=1,
            type_cotisation="All",
            prix=0,
        )
        self.assertAlmostEqual(
            self.user.end_connexion() - date,
            datetime.timedelta(days=2),
            delta=datetime.timedelta(seconds=1),
        )
