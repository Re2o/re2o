# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
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

from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.conf import settings
from django.utils.text import slugify

import tempfile
from subprocess import Popen, PIPE
import os


TEMP_PREFIX = getattr(settings, 'TEX_TEMP_PREFIX', 'render_tex-')
CACHE_PREFIX = getattr(settings, 'TEX_CACHE_PREFIX', 'render-tex')
CACHE_TIMEOUT = getattr(settings, 'TEX_CACHE_TIMEOUT', 86400)  # 1 day


def render_invoice(request, ctx={}):
    """
    Render an invoice using some available information such as the current
    date, the user, the articles, the prices, ...
    """
    filename = '_'.join([
        'invoice',
        slugify(ctx['asso_name']),
        slugify(ctx['recipient_name']),
        str(ctx['DATE'].year),
        str(ctx['DATE'].month),
        str(ctx['DATE'].day),
    ])
    r = render_tex(request, 'cotisations/factures.tex', ctx)
    r['Content-Disposition'] = 'attachment; filename="{name}.pdf"'.format(
        name=filename
    )
    return r


def render_tex(request, template, ctx={}):
    """
    Creates a PDF from a LaTex templates using pdflatex.
    Writes it in a temporary directory and send back an HTTP response for
    accessing this file.
    """
    context = Context(ctx)
    template = get_template(template)
    rendered_tpl = template.render(context).encode('utf-8')

    with tempfile.TemporaryDirectory() as tempdir:
        for i in range(2):
            process = Popen(
                ['pdflatex', '-output-directory', tempdir],
                stdin=PIPE,
                stdout=PIPE,
            )
            process.communicate(rendered_tpl)
        with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
            pdf = f.read()
    r = HttpResponse(content_type='application/pdf')
    r.write(pdf)
    return r
