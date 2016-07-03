# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz
# Gplv2
from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader
from django.contrib import messages
from django.db.models import Max
from django.utils import timezone

from users.models import User, Right, Ban, DelRightForm, UserForm, InfoForm, PasswordForm, StateForm, RightForm, BanForm, ProfilForm
from cotisations.models import Facture
from machines.models import Machine
from users.forms  import PassForm
from search.models import SearchForm
from cotisations.views import is_adherent, end_adhesion

from re2o.login import makeSecret, hashNT

def end_ban(user):
    """ Renvoie la date de fin de ban d'un user, False sinon """
    date_max = Ban.objects.all().filter(user=user).aggregate(Max('date_end'))['date_end__max']
    return date_max

def is_ban(user):
    """ Renvoie si un user est banni ou non """
    end = end_ban(user)
    if not end:
        return False
    elif end < timezone.now():
        return False
    else:
        return True 

def has_access(user):
   """ Renvoie si un utilisateur a accès à internet"""
   if user.state == User.STATE_ACTIVE and not is_ban(user) and is_adherent(user):
       return True
   else:
       return False

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
    if is_ban(user):
        messages.error(request, u"Attention, cet utilisateur a deja un bannissement actif" )
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
    connexion = []
    for user in users_list:
        connexion.append([user, has_access(user)])
    return render(request, 'users/index.html', {'users_list': connexion})

def profil(request):
    if request.method == 'POST':
        profil = ProfilForm(request.POST or None)
        if profil.is_valid():
            profils = profil.cleaned_data['user']
            users = User.objects.get(pseudo = profils)
            machines = None
            factures = Facture.objects.filter(user__pseudo = users)
            bans = Ban.objects.filter(user__pseudo = users)
            end = None
            if(is_ban(users)):
                end=end_ban(users)
            return render(request, 'users/profil.html', {'user': users, 'machine_list' :machines, 'facture_list':factures, 'ban_list':bans, 'end_ban':end, 'end_adhesion':end_adhesion(users), 'actif':has_access(users)})
        return redirect("/users/")
    return redirect("/users/")

