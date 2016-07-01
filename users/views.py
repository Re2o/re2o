# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz
# Gplv2
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader
from django.contrib import messages

from users.models import User, UserForm, InfoForm, PasswordForm, StateForm
from users.forms  import PassForm

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(template, c, context_instance=RequestContext(request))

def new_user(request):
    if request.method == 'POST':
        user = InfoForm(request.POST)
        if user.is_valid():
            user.save()
        return form({'userform': user}, 'users/user.html', request)
    else:
        user = InfoForm()
        return form({'userform': user}, 'users/user.html', request)

def edit_info(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, u"Utilisateur inexistant" )
        return redirect("/users/")
    user = InfoForm(request.POST or None, instance=user)
    if user.is_valid():
        user.save()
    return form({'userform': user}, 'users/user.html', request)

def state(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, u"Utilisateur inexistant" )
        return redirect("/users/")
    user = StateForm(request.POST or None, instance=user)
    if user.is_valid():
        user.save()
    return form({'userform': user}, 'users/user.html', request)

def password(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, u"Utilisateur inexistant" )
        return redirect("/users/")
    user_form = PassForm(request.POST or None)
    if user_form.is_valid():
        user.pwd_ssha = user_form.cleaned_data['passwd']
        user.pwd_ntlm = user_form.cleaned_data['passwd'] 
        user.save()
    return form({'userform': user_form}, 'users/user.html', request)
