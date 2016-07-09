from django.template.loader import get_template
from django.template import TemplateDoesNotExist, Context
from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import redirect

from tempfile import mkdtemp
import subprocess
import os
import shutil
from hashlib import md5


TEMP_PREFIX = getattr(settings, 'TEX_TEMP_PREFIX', 'render_tex-')
CACHE_PREFIX = getattr(settings, 'TEX_CACHE_PREFIX', 'render-tex')
CACHE_TIMEOUT = getattr(settings, 'TEX_CACHE_TIMEOUT', 86400)  # 1 day


def render_tex(request, template, ctx={}):
    doc = template.rsplit('/', 1)[-1].rsplit('.', 1)[0]

    # Utile ? Parfois il faut le chemin absolu pour retrouver les images
    #ctx.setdefault('tpl_path', os.path.join(settings.BASE_DIR, 'factures/templates/factures'))

    try:
        body = get_template(template).render(Context(ctx)).encode('utf-8')
    except TemplateDoesNotExist:
        raise Http404()

    etag = md5(body).hexdigest()
    if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
        return HttpResponseNotModified()

    cache_key = "%s:%s:%s" % (CACHE_PREFIX, template, etag)
    pdf = cache.get(cache_key)
    if pdf is None:
        if b'\\nonstopmode' not in body:
            raise ValueError("\\nonstopmode not present in document, cowardly refusing to process.")

        tmp = mkdtemp(prefix=TEMP_PREFIX)
        try:
            with open("%s/%s.tex" % (tmp, doc), "w") as f:
                f.write(str(body))
            del body

            error = subprocess.Popen(
                ["pdflatex", "%s.tex" % doc],
                cwd=tmp,
                stdin=open(os.devnull, "r"),
                stderr=open(os.devnull, "wb"),
                stdout=open(os.devnull, "wb")
            ).wait()

            if error:
                log = open("%s/%s.log" % (tmp, doc)).read()
                return HttpResponse(log, content_type="text/plain")

            pdf = open("%s/%s.pdf" % (tmp, doc)).read()
        finally:
            shutil.rmtree(tmp)
            pass

        if pdf:
            cache.set(cache_key, pdf, CACHE_TIMEOUT)

    res = HttpResponse(pdf, content_type="application/pdf")
    res['ETag'] = etag
    return res


