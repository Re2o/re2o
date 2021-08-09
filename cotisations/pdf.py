# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2021  Jean-Romain Garnier
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

"""pdf.py
Module in charge of rendering some HTML templates to generated PDF invoices.
"""


import os
import tempfile
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.text import slugify

from preferences.models import CotisationsOption

from xhtml2pdf import pisa
from django.contrib.staticfiles import finders


def render_invoice(_request, ctx={}):
    """
    Render an invoice using some available information such as the current
    date, the user, the articles, the prices, ...
    """
    options, _ = CotisationsOption.objects.get_or_create()
    is_estimate = ctx.get("is_estimate", False)
    filename = "_".join(
        [
            "cost_estimate" if is_estimate else "invoice",
            slugify(ctx.get("asso_name", "")),
            slugify(ctx.get("recipient_name", "")),
            str(ctx.get("DATE", datetime.now()).year),
            str(ctx.get("DATE", datetime.now()).month),
            str(ctx.get("DATE", datetime.now()).day),
        ]
    )
    templatename = options.invoice_template.template.name.split("/")[-1]
    r = render_pdf(_request, templatename, ctx, filename)
    return r


def render_voucher(_request, ctx={}):
    """
    Render a subscribtion voucher.
    """
    options, _ = CotisationsOption.objects.get_or_create()
    filename = "_".join(
        [
            "voucher",
            slugify(ctx.get("asso_name", "")),
            slugify(ctx.get("firstname", "")),
            slugify(ctx.get("lastname", "")),
            str(ctx.get("date_begin", datetime.now()).year),
            str(ctx.get("date_begin", datetime.now()).month),
            str(ctx.get("date_begin", datetime.now()).day),
        ]
    )
    templatename = options.voucher_template.template.name.split("/")[-1]
    r = render_pdf(_request, templatename, ctx, filename)
    return r


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    See https://xhtml2pdf.readthedocs.io/en/latest/usage.html#using-xhtml2pdf-in-django
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
            result = list(os.path.realpath(path) for path in result)
            path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # Make sure that file exists
    if not os.path.isfile(path):
        raise Exception("media URI must start with %s or %s" % (sUrl, mUrl))
    return path


def create_pdf(template, ctx={}):
    """Creates and returns a PDF from an HTML template using xhtml2pdf.

    It create a temporary file for the PDF then read it to return its content.

    Args:
        template: Path to the HTML template.
        ctx: Dict with the context for rendering the template.

    Returns:
        The content of the temporary PDF file generated.
    """
    context = ctx
    template = get_template(template)
    rendered_tpl = template.render(context).encode("utf-8")

    with tempfile.TemporaryFile("wb+") as tempf:
        pisa_status = pisa.CreatePDF(rendered_tpl, dest=tempf)

        if pisa_status.err:
            raise pisa_status.err

        tempf.seek(0)
        pdf = tempf.read()

    return pdf


def render_pdf(_request, template, ctx={}, filename="invoice"):
    """
    Creates a PDF from an HTML template using xhtml2pdf.

    Calls `create_pdf` and send back an HTTP response for accessing this file.

    Args:
        _request: Unused, but allow using this function as a Django view.
        template: Path to the HTML template.
        ctx: Dict with the context for rendering the template.
        filename: The name of the file to include in the request headers.

    Returns:
        The content of the temporary PDF file generated.
    """
    pdf = create_pdf(template, ctx)

    r = HttpResponse(content_type="application/pdf")
    r["Content-Disposition"] = 'attachment; filename="{name}.pdf"'.format(name=filename)
    r.write(pdf)

    return r
