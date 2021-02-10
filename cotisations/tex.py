# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
# Copyright © 2017  Augustin Lemesle
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
"""tex.py
Module in charge of rendering some LaTex templates.
Used to generated PDF invoice.
"""


import os
import tempfile
from datetime import datetime
from subprocess import PIPE, Popen

from django.conf import settings
from django.db import models
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.text import slugify

from preferences.models import CotisationsOption
from re2o.mixins import AclMixin, RevMixin

TEMP_PREFIX = getattr(settings, "TEX_TEMP_PREFIX", "render_tex-")
CACHE_PREFIX = getattr(settings, "TEX_CACHE_PREFIX", "render-tex")
CACHE_TIMEOUT = getattr(settings, "TEX_CACHE_TIMEOUT", 86400)  # 1 day


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
    r = render_tex(_request, templatename, ctx)
    r["Content-Disposition"] = 'attachment; filename="{name}.pdf"'.format(name=filename)
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
    r = render_tex(_request, templatename, ctx)
    r["Content-Disposition"] = 'attachment; filename="{name}.pdf"'.format(name=filename)
    return r


def create_pdf(template, ctx={}):
    """Creates and returns a PDF from a LaTeX template using pdflatex.

    It create a temporary file for the PDF then read it to return its content.

    Args:
        template: Path to the LaTeX template.
        ctx: Dict with the context for rendering the template.

    Returns:
        The content of the temporary PDF file generated.
    """
    context = ctx
    template = get_template(template)
    rendered_tpl = template.render(context).encode("utf-8")

    with tempfile.TemporaryDirectory() as tempdir:
        for _ in range(2):
            process = Popen(
                ["pdflatex", "-output-directory", tempdir],
                stdin=PIPE,
                stdout=PIPE,
            )
            process.communicate(rendered_tpl)
        with open(os.path.join(tempdir, "texput.pdf"), "rb") as f:
            pdf = f.read()

    return pdf


def escape_chars(string):
    """Escape the '%' and the '€' signs to avoid messing with LaTeX"""
    if not isinstance(string, str):
        return string
    mapping = (("€", r"\euro"), ("%", r"\%"))
    r = str(string)
    for k, v in mapping:
        r = r.replace(k, v)
    return r


def render_tex(_request, template, ctx={}):
    """Creates a PDF from a LaTex templates using pdflatex.

    Calls `create_pdf` and send back an HTTP response for
    accessing this file.

    Args:
        _request: Unused, but allow using this function as a Django view.
        template: Path to the LaTeX template.
        ctx: Dict with the context for rendering the template.

    Returns:
        An HttpResponse with type `application/pdf` containing the PDF file.
    """
    pdf = create_pdf(template, ctx)
    r = HttpResponse(content_type="application/pdf")
    r.write(pdf)
    return r
