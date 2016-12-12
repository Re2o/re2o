from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template.context_processors import csrf
from django.template import Context, RequestContext, loader
from re2o.settings import services_urls

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render(request, template, c)


def index(request):
    i = 0
    services = [{}]
    for key, s in services_urls.items():
        if len(services) <= i:
            services += [{}]
        services[i][key] = s
        i = i + 1 if i < 2 else 0

    return form({'services_urls': services}, 're2o/index.html', request)
