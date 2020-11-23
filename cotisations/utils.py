# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Hugo Levy-Falk
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

import os

from django.template.loader import get_template
from django.core.mail import EmailMessage
from re2o.mail_utils import send_mail_object

from .tex import create_pdf
from preferences.models import AssoOption, GeneralOption, CotisationsOption, Mandate
from re2o.settings import LOGO_PATH
from re2o import settings


def find_payment_method(payment):
    """Finds the payment method associated to the payment if it exists."""
    from cotisations.payment_methods import PAYMENT_METHODS

    for method in PAYMENT_METHODS:
        try:
            o = method.PaymentMethod.objects.get(payment=payment)
            return o
        except method.PaymentMethod.DoesNotExist:
            pass
    return None


def send_mail_invoice(invoice, request=None):
    """Creates the pdf of the invoice and sends it by email to the client"""
    purchases_info = []
    for purchase in invoice.vente_set.all():
        purchases_info.append(
            {
                "name": purchase.name,
                "price": purchase.prix,
                "quantity": purchase.number,
                "total_price": purchase.prix_total,
            }
        )

    ctx = {
        "paid": True,
        "fid": invoice.id,
        "DATE": invoice.date,
        "recipient_name": "{} {}".format(invoice.user.name, invoice.user.surname),
        "address": invoice.user.room,
        "article": purchases_info,
        "total": invoice.prix_total(),
        "asso_name": AssoOption.get_cached_value("name"),
        "line1": AssoOption.get_cached_value("adresse1"),
        "line2": AssoOption.get_cached_value("adresse2"),
        "siret": AssoOption.get_cached_value("siret"),
        "email": AssoOption.get_cached_value("contact"),
        "phone": AssoOption.get_cached_value("telephone"),
        "tpl_path": os.path.join(settings.BASE_DIR, LOGO_PATH),
    }

    template = CotisationsOption.get_cached_value("invoice_template").template.name.split("/")[-1]
    pdf = create_pdf(template, ctx)
    template = get_template("cotisations/email_invoice")

    ctx = {
        "name": "{} {}".format(invoice.user.name, invoice.user.surname),
        "contact_mail": AssoOption.get_cached_value("contact"),
        "asso_name": AssoOption.get_cached_value("name"),
    }

    mail = EmailMessage(
        "Votre facture / Your invoice",
        template.render(ctx),
        GeneralOption.get_cached_value("email_from"),
        [invoice.user.get_mail],
        attachments=[("invoice.pdf", pdf, "application/pdf")],
    )

    send_mail_object(mail, request)


def send_mail_voucher(invoice, request=None):
    """Creates a voucher from an invoice and sends it by email to the client"""
    president = Mandate.get_mandate(invoice.date).president
    ctx = {
        "asso_name": AssoOption.get_cached_value("name"),
        "pres_name": " ".join([president.name, president.surname]),
        "firstname": invoice.user.name,
        "lastname": invoice.user.surname,
        "email": invoice.user.email,
        "phone": invoice.user.telephone,
        "date_end": invoice.get_subscription().latest("date_end").date_end_memb,
        "date_begin": invoice.get_subscription().earliest("date_start").date_start_memb,
    }
    templatename = CotisationsOption.get_cached_value(
        "voucher_template"
    ).template.name.split("/")[-1]
    pdf = create_pdf(templatename, ctx)
    template = get_template("cotisations/email_subscription_accepted")

    ctx = {
        "name": "{} {}".format(invoice.user.name, invoice.user.surname),
        "asso_email": AssoOption.get_cached_value("contact"),
        "asso_name": AssoOption.get_cached_value("name"),
        "date_end": invoice.get_subscription().latest("date_end_memb").date_end_memb,
    }

    mail = EmailMessage(
        "Votre reçu / Your voucher",
        template.render(ctx),
        GeneralOption.get_cached_value("email_from"),
        [invoice.user.get_mail],
        attachments=[("voucher.pdf", pdf, "application/pdf")],
    )

    send_mail_object(mail, request)
