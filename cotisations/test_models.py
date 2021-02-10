import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone

from users.models import User

from .models import Cotisation, Facture, Paiement, Vente


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
        Add one day of membership and one day of connection.
        """
        date = timezone.now()
        purchase = Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration_connection=0,
            duration_days_connection=1,
            duration_membership=0,
            duration_days_membership=1,
            prix=0,
        )
        self.f.reorder_purchases()
        self.assertAlmostEqual(
            self.user.end_connexion() - date,
            datetime.timedelta(days=1),
            delta=datetime.timedelta(seconds=1),
        )
        self.assertAlmostEqual(
            self.user.end_adhesion() - date,
            datetime.timedelta(days=1),
            delta=datetime.timedelta(seconds=1),
        )

    def test_one_month_cotisation(self):
        """
        It should be possible to have one day membership.
        Add one mounth of membership and one mounth of connection
        """
        date = timezone.now()
        Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration_connection=1,
            duration_days_connection=0,
            duration_membership=1,
            duration_days_membership=0,
            prix=0,
        )
        self.f.reorder_purchases()
        end_con = self.user.end_connexion()
        end_memb = self.user.end_adhesion()
        expected_end = date + relativedelta(months=1)
        self.assertEqual(end_con.day, expected_end.day)
        self.assertEqual(end_con.month, expected_end.month)
        self.assertEqual(end_con.year, expected_end.year)
        self.assertEqual(end_memb.day, expected_end.day)
        self.assertEqual(end_memb.month, expected_end.month)
        self.assertEqual(end_memb.year, expected_end.year)

    def test_one_month_and_one_week_cotisation(self):
        """
        It should be possible to have one day membership.
        Add one mounth and one week of membership and one mounth
        and one week of connection
        """
        date = timezone.now()
        Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration_connection=1,
            duration_days_connection=7,
            duration_membership=1,
            duration_days_membership=7,
            prix=0,
        )
        self.f.reorder_purchases()
        end_con = self.user.end_connexion()
        end_memb = self.user.end_adhesion()
        expected_end = date + relativedelta(months=1, days=7)
        self.assertEqual(end_con.day, expected_end.day)
        self.assertEqual(end_con.month, expected_end.month)
        self.assertEqual(end_con.year, expected_end.year)
        self.assertEqual(end_memb.day, expected_end.day)
        self.assertEqual(end_memb.month, expected_end.month)
        self.assertEqual(end_memb.year, expected_end.year)

    def test_date_start_cotisation(self):
        """
        It should be possible to add a cotisation with a specific start date
        """
        v = Vente(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration_connection=0,
            duration_days_connection=1,
            duration_membership=0,
            duration_deys_membership=1,
            prix=0,
        )
        v.create_cotis(
            date_start_con=timezone.make_aware(datetime.datetime(1998, 10, 16)),
            date_start_memb=timezone.make_aware(datetime.datetime(1998, 10, 16)),
        )
        v.save()
        self.assertEqual(
            v.cotisation.date_end_con,
            timezone.make_aware(datetime.datetime(1998, 10, 17)),
        )
        self.assertEqual(
            v.cotisation.date_end_memb,
            timezone.make_aware(datetime.datetime(1998, 10, 17)),
        )

    def test_one_day_cotisation_membership_only(self):
        """
        It should be possible to have one day membership without connection.
        Add one day of membership and no connection.
        """
        date = timezone.now()
        purchase = Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration_connection=0,
            duration_days_connection=0,
            duration_membership=0,
            duration_days_membership=1,
            prix=0,
        )
        self.f.reorder_purchases()
        self.assertEqual(
            self.user.end_connexion(),
            None,
        )
        self.assertAlmostEqual(
            self.user.end_adhesion() - date,
            datetime.timedelta(days=1),
            delta=datetime.timedelta(seconds=1),
        )

    def test_one_month_cotisation_membership_only(self):
        """
        It should be possible to have one month membership.
        Add one mounth of membership and no connection
        """
        date = timezone.now()
        Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration_connection=0,
            duration_days_connection=0,
            duration_membership=1,
            duration_days_membership=0,
            prix=0,
        )
        self.f.reorder_purchases()
        end_con = self.user.end_connexion()
        end_memb = self.user.end_adhesion()
        expected_end = date + relativedelta(months=1)
        self.assertEqual(end_con, None)
        self.assertEqual(end_memb.day, expected_end.day)
        self.assertEqual(end_memb.month, expected_end.month)
        self.assertEqual(end_memb.year, expected_end.year)

    def test_one_month_and_one_week_cotisation_membership_only(self):
        """
        It should be possible to have one mounth and one week  membership.
        Add one mounth and one week of membership and no connection.
        """
        date = timezone.now()
        Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration_connection=0,
            duration_days_connection=0,
            duration_membership=1,
            duration_days_membership=7,
            prix=0,
        )
        self.f.reorder_purchases()
        end_con = self.user.end_connexion()
        end_memb = self.user.end_adhesion()
        expected_end = date + relativedelta(months=1, days=7)
        self.assertEqual(end_con, None)
        self.assertEqual(end_memb.day, expected_end.day)
        self.assertEqual(end_memb.month, expected_end.month)
        self.assertEqual(end_memb.year, expected_end.year)

    def test_date_start_cotisation_membership_only(self):
        """
        It should be possible to add a cotisation with a specific start date
        """
        v = Vente(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration_connection=0,
            duration_days_connection=0,
            duration_membership=0,
            duration_days_membership=1,
            prix=0,
        )
        v.create_cotis(
            date_start_con=timezone.make_aware(datetime.datetime(1998, 10, 16)),
            date_start_memb=timezone.make_aware(datetime.datetime(1998, 10, 16)),
        )
        v.save()
        self.assertEqual(
            v.cotisation.date_end_con,
            timezone.make_aware(datetime.datetime(1998, 10, 17)),
        )
        self.assertEqual(
            v.cotisation.date_end_memb,
            timezone.make_aware(datetime.datetime(1998, 10, 16)),
        )

    def test_cotisation_membership_diff_connection(self):
        """
        It should be possible to have purchase a membership longer
        than the connection.
        """
        date = timezone.now()
        Vente.objects.create(
            facture=self.f,
            number=1,
            name="Test purchase",
            duration_connection=1,
            duration_days_connection=0,
            duration_membership=2,
            duration_days_membership=0,
            prix=0,
        )
        self.f.reorder_purchases()
        end_con = self.user.end_connexion()
        end_memb = self.user.end_adhesion()
        expected_end_con = date + relativedelta(months=1)
        expected_end_memb = date + relativedelta(months=2)
        self.assertEqual(end_con.day, expected_end_con.day)
        self.assertEqual(end_con.month, expected_end_con.month)
        self.assertEqual(end_con.year, expected_end_con.year)
        self.assertEqual(end_memb.day, expected_end_memb.day)
        self.assertEqual(end_memb.month, expected_end_memb.month)
        self.assertEqual(end_memb.year, expected_end_memb.year)

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
            duration_connection=1,
            duration_days_connection=0,
            duration_membership=1,
            duration_days_membership=0,
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
            duration_connection=1,
            duration_days_connection=0,
            duration_membership=1,
            duration_days_membership=0,
            prix=0,
        )
        invoice1.reorder_purchases()
        delta_con = relativedelta(self.user.end_connexion(), date)
        delta_memb = relativedelta(self.user.end_adhesion(), date)
        delta_con.microseconds = 0
        delta_memb.microseconds = 0
        try:
            self.assertEqual(delta_con, relativedelta(months=2))
            self.assertEqual(delta_memb, relativedelta(months=2))
        except Exception as e:
            invoice1.delete()
            invoice2.delete()
            raise e
        invoice1.delete()
        invoice2.delete()
