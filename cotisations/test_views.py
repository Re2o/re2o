import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from users.models import Adherent

from .models import Article, Cotisation, Facture, Paiement, Vente


class NewFactureTests(TestCase):
    def tearDown(self):
        self.user.facture_set.all().delete()
        self.user.delete()
        self.paiement.delete()
        self.article_one_day.delete()
        self.article_one_month.delete()
        self.article_one_month_and_one_week.delete()

    def setUp(self):
        self.user = Adherent.objects.create(pseudo="testUser", email="test@example.org")
        self.user.set_password("plopiplop")
        self.user.user_permissions.set(
            [
                Permission.objects.get_by_natural_key(
                    "add_facture", "cotisations", "Facture"
                ),
                Permission.objects.get_by_natural_key(
                    "use_every_payment", "cotisations", "Paiement"
                ),
            ]
        )
        self.user.save()

        self.paiement = Paiement.objects.create(moyen="test payment")
        self.article_one_day = Article.objects.create(
            name="One day",
            prix=0,
            duration_connection=0,
            duration_days_connection=1,
            duration_membership=0,
            duration_days_membership=1,
            available_for_everyone=True,
        )
        self.article_one_month = Article.objects.create(
            name="One mounth",
            prix=0,
            duration_connection=1,
            duration_days_connection=0,
            duration_membership=1,
            duration_days_membership=0,
            available_for_everyone=True,
        )
        self.article_one_month_and_one_week = Article.objects.create(
            name="One mounth and one week",
            prix=0,
            duration_connection=1,
            duration_days_connection=7,
            duration_membership=1,
            duration_days_membership=7,
            available_for_everyone=True,
        )
        self.client.login(username="testUser", password="plopiplop")

    def test_invoice_with_one_day(self):
        data = {
            "Facture-paiement": self.paiement.pk,
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,
            "form-0-article": 1,
            "form-0-quantity": 1,
        }
        date = timezone.now()
        response = self.client.post(
            reverse("cotisations:new-facture", kwargs={"userid": self.user.pk}), data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/profil/%d" % self.user.pk)
        self.assertAlmostEqual(
            self.user.end_connexion() - date,
            datetime.timedelta(days=1),
            delta=datetime.timedelta(seconds=1),
        )

    def test_invoice_with_one_month(self):
        data = {
            "Facture-paiement": self.paiement.pk,
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,
            "form-0-article": 2,
            "form-0-quantity": 1,
        }
        date = timezone.now()
        response = self.client.post(
            reverse("cotisations:new-facture", kwargs={"userid": self.user.pk}), data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/profil/%d" % self.user.pk)
        delta = relativedelta(self.user.end_connexion(), date)
        delta.microseconds = 0
        self.assertEqual(delta, relativedelta(months=1))

    def test_invoice_with_one_month_and_one_week(self):
        data = {
            "Facture-paiement": self.paiement.pk,
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,
            "form-0-article": 1,
            "form-0-quantity": 7,
            "form-1-article": 2,
            "form-1-quantity": 1,
        }
        date = timezone.now()
        response = self.client.post(
            reverse("cotisations:new-facture", kwargs={"userid": self.user.pk}), data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/profil/%d" % self.user.pk)
        invoice = self.user.facture_set.first()
        delta = relativedelta(self.user.end_connexion(), date)
        delta.microseconds = 0
        self.assertEqual(delta, relativedelta(months=1, days=7))

    def test_several_articles_creates_several_purchases(self):
        data = {
            "Facture-paiement": self.paiement.pk,
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,
            "form-0-article": 2,
            "form-0-quantity": 1,
            "form-1-article": 2,
            "form-1-quantity": 1,
        }
        response = self.client.post(
            reverse("cotisations:new-facture", kwargs={"userid": self.user.pk}), data
        )
        f = self.user.facture_set.first()
        self.assertEqual(f.vente_set.count(), 2)
