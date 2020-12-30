# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import re2o.mixins
import re2o.aes_field
import re2o.field_permissions
import cotisations.models
import cotisations.payment_methods.mixins


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    replaces = [
        ("cotisations", "0001_initial"),
        ("cotisations", "0002_remove_facture_article"),
        ("cotisations", "0003_auto_20160702_1448"),
        ("cotisations", "0004_auto_20160702_1528"),
        ("cotisations", "0005_auto_20160702_1532"),
        ("cotisations", "0006_auto_20160702_1534"),
        ("cotisations", "0007_auto_20160702_1543"),
        ("cotisations", "0008_auto_20160702_1614"),
        ("cotisations", "0009_remove_cotisation_user"),
        ("cotisations", "0010_auto_20160702_1840"),
        ("cotisations", "0011_auto_20160702_1911"),
        ("cotisations", "0012_auto_20160704_0118"),
        ("cotisations", "0013_auto_20160711_2240"),
        ("cotisations", "0014_auto_20160712_0245"),
        ("cotisations", "0015_auto_20160714_2142"),
        ("cotisations", "0016_auto_20160715_0110"),
        ("cotisations", "0017_auto_20170718_2329"),
        ("cotisations", "0018_paiement_type_paiement"),
        ("cotisations", "0019_auto_20170819_0055"),
        ("cotisations", "0020_auto_20170819_0057"),
        ("cotisations", "0021_auto_20170819_0104"),
        ("cotisations", "0022_auto_20170824_0128"),
        ("cotisations", "0023_auto_20170902_1303"),
        ("cotisations", "0024_auto_20171015_2033"),
        ("cotisations", "0025_article_type_user"),
        ("cotisations", "0026_auto_20171028_0126"),
        ("cotisations", "0027_auto_20171029_1156"),
        ("cotisations", "0028_auto_20171231_0007"),
        ("cotisations", "0029_auto_20180414_2056"),
        ("cotisations", "0030_custom_payment"),
        ("cotisations", "0031_comnpaypayment_production"),
        ("cotisations", "0032_custom_invoice"),
        ("cotisations", "0033_auto_20180818_1319"),
        ("cotisations", "0034_auto_20180831_1532"),
        ("cotisations", "0035_notepayment"),
        ("cotisations", "0036_custominvoice_remark"),
        ("cotisations", "0037_costestimate"),
        ("cotisations", "0038_auto_20181231_1657"),
        ("cotisations", "0039_freepayment"),
        ("cotisations", "0040_auto_20191002_2335"),
        ("cotisations", "0041_auto_20191103_2131"),
        ("cotisations", "0042_auto_20191120_0159"),
        ("cotisations", "0043_separation_membership_connection_p1"),
        ("cotisations", "0044_separation_membership_connection_p2"),
        ("cotisations", "0045_separation_membership_connection_p3"),
        ("cotisations", "0046_article_need_membership"),
        ("cotisations", "0047_article_need_membership_init"),
        ("cotisations", "0048_auto_20201017_0018"),
        ("cotisations", "0049_auto_20201102_2305"),
        ("cotisations", "0050_auto_20201102_2342"),
        ("cotisations", "0051_auto_20201228_1636"),
    ]
    operations = [
        migrations.CreateModel(
            name="BaseInvoice",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateTimeField(auto_now_add=True, verbose_name="Date")),
            ],
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                re2o.field_permissions.FieldPermissionModelMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="Facture",
            fields=[
                (
                    "baseinvoice_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="cotisations.BaseInvoice",
                    ),
                ),
                (
                    "cheque",
                    models.CharField(
                        max_length=255, blank=True, verbose_name="cheque number"
                    ),
                ),
                ("valid", models.BooleanField(default=False, verbose_name="validated")),
                (
                    "control",
                    models.BooleanField(default=False, verbose_name="controlled"),
                ),
            ],
            options={
                "permissions": (
                    ("change_facture_control", 'Can edit the "controlled" state'),
                    ("view_facture", "Can view an invoice object"),
                    ("change_all_facture", "Can edit all the previous invoices"),
                ),
                "verbose_name": "invoice",
                "verbose_name_plural": "invoices",
            },
        ),
        migrations.CreateModel(
            name="CustomInvoice",
            fields=[
                (
                    "baseinvoice_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="cotisations.BaseInvoice",
                    ),
                ),
                (
                    "recipient",
                    models.CharField(max_length=255, verbose_name="Recipient"),
                ),
                (
                    "payment",
                    models.CharField(max_length=255, verbose_name="Payment type"),
                ),
                ("address", models.CharField(max_length=255, verbose_name="Address")),
                ("paid", models.BooleanField(verbose_name="Paid")),
                (
                    "remark",
                    models.TextField(verbose_name="remark", blank=True, null=True),
                ),
            ],
            bases=("cotisations.baseinvoice",),
            options={
                "permissions": (("view_custominvoice", "Can view a custom invoice"),)
            },
        ),
        migrations.CreateModel(
            name="CostEstimate",
            fields=[
                (
                    "custominvoice_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="cotisations.CustomInvoice",
                    ),
                ),
                (
                    "validity",
                    models.DurationField(
                        verbose_name="Period of validity", help_text="DD HH:MM:SS"
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_costestimate", "Can view a cost estimate object"),
                )
            },
            bases=("cotisations.custominvoice",),
        ),
        migrations.CreateModel(
            name="Vente",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "number",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="amount",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="article")),
                (
                    "prix",
                    models.DecimalField(
                        max_digits=5, decimal_places=2, verbose_name="price"
                    ),
                ),
                (
                    "duration_connection",
                    models.PositiveIntegerField(
                        default=0, verbose_name="duration of the connection (in months)"
                    ),
                ),
                (
                    "duration_days_connection",
                    models.PositiveIntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="duration of the connection (in days, will be added to duration in months)",
                    ),
                ),
                (
                    "duration_membership",
                    models.PositiveIntegerField(
                        default=0, verbose_name="duration of the membership (in months)"
                    ),
                ),
                (
                    "duration_days_membership",
                    models.PositiveIntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="duration of the membership (in days, will be added to duration in months)",
                    ),
                ),
            ],
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                models.Model,
            ),
            options={
                "permissions": (
                    ("view_vente", "Can view a purchase object"),
                    ("change_all_vente", "Can edit all the previous purchases"),
                ),
                "verbose_name": "purchase",
                "verbose_name_plural": "purchases",
            },
        ),
        migrations.CreateModel(
            name="Article",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=255, verbose_name="designation"),
                ),
                (
                    "prix",
                    models.DecimalField(
                        max_digits=5, decimal_places=2, verbose_name="unit price"
                    ),
                ),
                (
                    "duration_connection",
                    models.PositiveIntegerField(
                        default=0, verbose_name="duration of the connection (in months)"
                    ),
                ),
                (
                    "duration_days_connection",
                    models.PositiveIntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="duration of the connection (in days, will be added to duration in months)",
                    ),
                ),
                (
                    "duration_membership",
                    models.PositiveIntegerField(
                        default=0, verbose_name="duration of the membership (in months)"
                    ),
                ),
                (
                    "duration_days_membership",
                    models.PositiveIntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="duration of the membership (in days, will be added to duration in months)",
                    ),
                ),
                (
                    "need_membership",
                    models.BooleanField(
                        default=True, verbose_name="need membership to be purchased"
                    ),
                ),
                (
                    "type_user",
                    models.CharField(
                        choices=[
                            ("Adherent", "Member"),
                            ("Club", "Club"),
                            ("All", "Both of them"),
                        ],
                        default="All",
                        max_length=255,
                        verbose_name="type of users concerned",
                    ),
                ),
                (
                    "available_for_everyone",
                    models.BooleanField(
                        default=False, verbose_name="is available for every user"
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_article", "Can view an article object"),
                    ("buy_every_article", "Can buy every article"),
                ),
                "verbose_name": "article",
                "verbose_name_plural": "articles",
            },
        ),
        migrations.CreateModel(
            name="Banque",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "permissions": (("view_banque", "Can view a bank object"),),
                "verbose_name": "bank",
                "verbose_name_plural": "banks",
            },
        ),
        migrations.CreateModel(
            name="Paiement",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("moyen", models.CharField(max_length=255, verbose_name="method")),
                (
                    "available_for_everyone",
                    models.BooleanField(
                        default=False,
                        verbose_name="is available for every user",
                    ),
                ),
                (
                    "is_balance",
                    models.BooleanField(
                        default=False,
                        editable=False,
                        verbose_name="is user balance",
                        help_text="There should be only one balance payment method.",
                        validators=[cotisations.models.check_no_balance],
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("view_paiement", "Can view a payment method object"),
                    ("use_every_payment", "Can use every payment method"),
                ),
                "verbose_name": "payment method",
                "verbose_name_plural": "payment methods",
            },
        ),
        migrations.CreateModel(
            name="Cotisation",
            bases=(
                re2o.mixins.RevMixin,
                re2o.mixins.AclMixin,
                models.Model,
            ),
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_start_con",
                    models.DateTimeField(verbose_name="start date for the connection"),
                ),
                (
                    "date_end_con",
                    models.DateTimeField(verbose_name="end date for the connection"),
                ),
                (
                    "date_start_memb",
                    models.DateTimeField(verbose_name="start date for the membership"),
                ),
                (
                    "date_end_memb",
                    models.DateTimeField(verbose_name="end date for the membership"),
                ),
            ],
            options={
                "permissions": (
                    ("view_cotisation", "Can view a subscription object"),
                    ("change_all_cotisation", "Can edit the previous subscriptions"),
                ),
                "verbose_name": "subscription",
                "verbose_name_plural": "subscriptions",
            },
        ),
        migrations.CreateModel(
            name="BalancePayment",
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin, models.Model),
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "minimum_balance",
                    models.DecimalField(
                        verbose_name="minimum balance",
                        help_text="The minimal amount of money allowed for the balance at the end of a payment. You can specify a negative amount.",
                        max_digits=5,
                        decimal_places=2,
                        default=0,
                    ),
                ),
                (
                    "maximum_balance",
                    models.DecimalField(
                        verbose_name="maximum balance",
                        help_text="The maximal amount of money allowed for the balance.",
                        max_digits=5,
                        decimal_places=2,
                        default=50,
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "credit_balance_allowed",
                    models.BooleanField(
                        verbose_name="allow user to credit their balance", default=False
                    ),
                ),
            ],
            options={"verbose_name", "user balance"},
        ),
        migrations.CreateModel(
            name="ChequePayment",
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin, models.Model),
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={"verbose_name", "cheque"},
        ),
        migrations.CreateModel(
            name="ComnpayPayment",
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin, models.Model),
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "payment_credential",
                    models.CharField(
                        max_length=255,
                        default="",
                        blank=True,
                        verbose_name="ComNpay VAT Number",
                    ),
                ),
                (
                    "payment_pass",
                    re2o.aes_field.AESEncryptedField(
                        max_length=255,
                        null=True,
                        blank=True,
                        verbose_name="ComNpay secret key",
                    ),
                ),
                (
                    "minimum_payment",
                    models.DecimalField(
                        verbose_name="minimum payment",
                        help_text="The minimal amount of money you have to use when paying with ComNpay.",
                        max_digits=5,
                        decimal_places=2,
                        default=1,
                    ),
                ),
                (
                    "production",
                    models.BooleanField(
                        default=True,
                        verbose_name="production mode enabled (production URL, instead of homologation)",
                    ),
                ),
            ],
            options={"verbose_name", "ComNpay"},
        ),
        migrations.CreateModel(
            name="FreePayment",
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin, models.Model),
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={"verbose_name", "Free payment"},
        ),
        migrations.CreateModel(
            name="NotePayment",
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin, models.Model),
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("server", models.CharField(max_length=255, verbose_name="server")),
                ("port", models.PositiveIntegerField(blank=True, null=True)),
                ("id_note", models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={"verbose_name", "NoteKfet"},
        ),
    ]
