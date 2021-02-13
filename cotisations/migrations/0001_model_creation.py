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
                ("date", models.DateTimeField(auto_now_add=True, verbose_name="date")),
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
                    models.CharField(max_length=255, verbose_name="recipient"),
                ),
                (
                    "payment",
                    models.CharField(max_length=255, verbose_name="payment type"),
                ),
                ("address", models.CharField(max_length=255, verbose_name="address")),
                ("paid", models.BooleanField(default=False, verbose_name="paid")),
                (
                    "remark",
                    models.TextField(verbose_name="remark", blank=True, null=True),
                ),
            ],
            bases=("cotisations.baseinvoice",),
            options={
                "permissions": (
                    ("view_custominvoice", "Can view a custom invoice object"),
                )
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
                        verbose_name="period of validity", help_text="DD HH:MM:SS"
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
                        verbose_name="duration of the connection (in months)"
                    ),
                ),
                (
                    "duration_days_connection",
                    models.PositiveIntegerField(
                        verbose_name="duration of the connection (in days, will be added to duration in months)",
                    ),
                ),
                (
                    "duration_membership",
                    models.PositiveIntegerField(
                        verbose_name="duration of the membership (in months)"
                    ),
                ),
                (
                    "duration_days_membership",
                    models.PositiveIntegerField(
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
            options={"verbose_name": "user balance"},
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
            options={"verbose_name": "cheque"},
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
            options={"verbose_name": "ComNpay"},
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
            options={"verbose_name": "Free payment"},
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
            options={"verbose_name": "NoteKfet"},
        ),
    ]
