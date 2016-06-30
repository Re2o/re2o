# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz
# Gplv2
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader

from users.models import UserForm, InfoForm


def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(template, c, context_instance=RequestContext(request))

def new_user(request):
    if request.method == 'POST':
        user = InfoForm(request.POST)
        if user.is_valid():
            user.save()
        return form({'userform': user}, 'users/new_user.html', request)
    else:
        user = InfoForm()
        return form({'userform': user}, 'users/new_user.html', request)
