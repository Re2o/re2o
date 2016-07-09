from django.template.loader import get_template
from django.template import TemplateDoesNotExist, Context
from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import redirect

import tempfile
from subprocess import Popen, PIPE
import os
import shutil
from hashlib import md5


TEMP_PREFIX = getattr(settings, 'TEX_TEMP_PREFIX', 'render_tex-')
CACHE_PREFIX = getattr(settings, 'TEX_CACHE_PREFIX', 'render-tex')
CACHE_TIMEOUT = getattr(settings, 'TEX_CACHE_TIMEOUT', 86400)  # 1 day


def render_tex(request,tmp, ctx={}):
    context = Context(ctx)
    template = get_template('cotisations/factures.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    
    with tempfile.TemporaryDirectory() as tempdir:
        for i in range(2):
            process = Popen(
                ['pdflatex', '-output-directory', tempdir],
                stdin = PIPE,
                stdout = PIPE,
            )
            process.communicate(rendered_tpl)
        with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
            pdf = f.read()
    r = HttpResponse(content_type='application/pdf')
    #r['Content-Disposition'] = 'attachement; filename=texput.pdf' 
    r.write(pdf)
    return r
