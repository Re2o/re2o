# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz
# Gplv2
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader
from django.contrib import messages

from users.models import User, Right, Ban, DelRightForm, UserForm, InfoForm, PasswordForm, StateForm, RightForm, BanForm
from users.forms  import PassForm

from re2o.login import makeSecret, hashNT

def end_ban(user):
    """ Renvoie la date de fin de ban d'un user, False sinon """
    date_max = Ban.objects.all().filter(user=user).aggregate(Max('date_end'))['date_end__max']
    return date_max

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(template, c, context_instance=RequestContext(request))

def new_user(request):
    user = InfoForm(request.POST or None)
    if user.is_valid():
        user.save()
        messages.success(request, "L'utilisateur a été crée")
        return redirect("/users/")
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
        messages.success(request, "L'user a bien été modifié")
        return redirect("/users/")
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
        messages.success(request, "Etat changé avec succès")
        return redirect("/users/")
    return form({'userform': user}, 'users/user.html', request)

def password(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, u"Utilisateur inexistant" )
        return redirect("/users/")
    user_form = PassForm(request.POST or None)
    if user_form.is_valid():
        if user_form.cleaned_data['passwd1'] != user_form.cleaned_data['passwd2']:
            messages.error(request, u"Les 2 mots de passe différent" )
            return form({'userform': user_form}, 'users/user.html', request)
        user.pwd_ssha = makeSecret(user_form.cleaned_data['passwd1'])
        user.pwd_ntlm = hashNT(user_form.cleaned_data['passwd1'])
        user.save()
        messages.success(request, "Le mot de passe a changé")
        return redirect("/users/")
    return form({'userform': user_form}, 'users/user.html', request)

def add_right(request):
    right = RightForm(request.POST or None)
    if right.is_valid():
        right.save()
        messages.success(request, "Droit ajouté")
        return redirect("/users/")
    return form({'userform': right}, 'users/user.html', request)

def del_right(request):
    right = DelRightForm(request.POST or None)
    if right.is_valid():
        right_del = right.cleaned_data['rights']
        right_del.delete()
        messages.success(request, "Droit retiré avec succès")
        return redirect("/users/")
    return form({'userform': right}, 'users/user.html', request)

def add_ban(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, u"Utilisateur inexistant" )
        return redirect("/users/")
    ban_instance = Ban(user=user)
    ban = BanForm(request.POST or None, instance=ban_instance)
    if ban.is_valid():
        ban.save()
        messages.success(request, "Bannissement ajouté")
        return redirect("/users/")
    return form({'userform': ban}, 'users/user.html', request)

def edit_ban(request, banid):
    try:
        ban_instance = Ban.objects.get(pk=banid)
    except User.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/users/")
    ban = BanForm(request.POST or None, instance=ban_instance)
    if ban.is_valid():
        ban.save()
        messages.success(request, "Bannissement modifié")
        return redirect("/users/")
    return form({'userform': ban}, 'users/user.html', request)

def index(request):
    users_list = User.objects.order_by('pk')
    return render(request, 'users/index.html', {'users_list': users_list})
