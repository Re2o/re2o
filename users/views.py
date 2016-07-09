# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz
# Gplv2
from django.shortcuts import render_to_response, render, redirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Max, ProtectedError
from django.db import IntegrityError
from django.utils import timezone

from users.models import User, Right, Ban, Whitelist, School
from users.models import DelRightForm, BanForm, WhitelistForm, DelSchoolForm
from users.models import InfoForm, StateForm, RightForm, SchoolForm
from cotisations.models import Facture
from machines.models import Machine, Interface
from users.forms import PassForm
from cotisations.views import is_adherent, end_adhesion
from machines.views import unassign_ips, assign_ips

from re2o.login import hashNT


def archive(user):
    """ Archive un utilisateur """
    unassign_ips(user)
    return


def unarchive(user):
    """ Triger actions au desarchivage d'un user """
    assign_ips(user)
    return


def end_ban(user):
    """ Renvoie la date de fin de ban d'un user, False sinon """
    date_max = Ban.objects.all().filter(
        user=user).aggregate(Max('date_end'))['date_end__max']
    return date_max


def end_whitelist(user):
    """ Renvoie la date de fin de ban d'un user, False sinon """
    date_max = Whitelist.objects.all().filter(
        user=user).aggregate(Max('date_end'))['date_end__max']
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


def is_whitelisted(user):
    """ Renvoie si un user est whitelisté ou non """
    end = end_whitelist(user)
    if not end:
        return False
    elif end < timezone.now():
        return False
    else:
        return True


def has_access(user):
    """ Renvoie si un utilisateur a accès à internet """
    return user.state == User.STATE_ACTIVE \
        and not is_ban(user) and (is_adherent(user) or is_whitelisted(user))


def is_active(interface):
    """ Renvoie si une interface doit avoir accès ou non """
    machine = interface.machine
    user = machine.user
    return machine.active and has_access(user)


def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(
        template,
        c,
        context_instance=RequestContext(request)
    )

@login_required
def new_user(request):
    user = InfoForm(request.POST or None)
    if user.is_valid():
        user.save()
        messages.success(request, "L'utilisateur a été crée")
        return redirect("/users/")
    return form({'userform': user}, 'users/user.html', request)

@login_required
def edit_info(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    user = InfoForm(request.POST or None, instance=user)
    if user.is_valid():
        user.save()
        messages.success(request, "L'user a bien été modifié")
        return redirect("/users/profil/" + userid)
    return form({'userform': user}, 'users/user.html', request)

@login_required
def state(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    state = StateForm(request.POST or None, instance=user)
    if state.is_valid():
        if state.has_changed():
            if state.cleaned_data['state'] == User.STATE_ARCHIVED:
                archive(user)
            else:
                unarchive(user)
        state.save()
        messages.success(request, "Etat changé avec succès")
        return redirect("/users/profil/" + userid)
    return form({'userform': state}, 'users/user.html', request)

@login_required
def password(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    u_form = PassForm(request.POST or None)
    if u_form.is_valid():
        if u_form.cleaned_data['passwd1'] != u_form.cleaned_data['passwd2']:
            messages.error(request, "Les 2 mots de passe différent")
            return form({'userform': u_form}, 'users/user.html', request)
        user.set_password(u_form.cleaned_data['passwd1'])
        user.pwd_ntlm = hashNT(u_form.cleaned_data['passwd1'])
        user.save()
        messages.success(request, "Le mot de passe a changé")
        return redirect("/users/profil/" + userid)
    return form({'userform': u_form}, 'users/user.html', request)

@login_required
@permission_required('bureau')
def add_right(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    right = RightForm(request.POST or None)
    if right.is_valid():
        right = right.save(commit=False)
        right.user = user
        try:
            right.save()
            messages.success(request, "Droit ajouté")
        except IntegrityError:
            pass
        return redirect("/users/profil/" + userid)
    return form({'userform': right}, 'users/user.html', request)

@login_required
@permission_required('bureau')
def del_right(request):
    right = DelRightForm(request.POST or None)
    if right.is_valid():
        right_del = right.cleaned_data['rights']
        right_del.delete()
        messages.success(request, "Droit retiré avec succès")
        return redirect("/users/")
    return form({'userform': right}, 'users/user.html', request)

@login_required
def add_ban(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    ban_instance = Ban(user=user)
    ban = BanForm(request.POST or None, instance=ban_instance)
    if ban.is_valid():
        ban.save()
        messages.success(request, "Bannissement ajouté")
        return redirect("/users/profil/" + userid)
    if is_ban(user):
        messages.error(
            request,
            "Attention, cet utilisateur a deja un bannissement actif"
        )
    return form({'userform': ban}, 'users/user.html', request)

@login_required
def edit_ban(request, banid):
    try:
        ban_instance = Ban.objects.get(pk=banid)
    except Ban.DoesNotExist:
        messages.error(request, "Entrée inexistante")
        return redirect("/users/")
    ban = BanForm(request.POST or None, instance=ban_instance)
    if ban.is_valid():
        ban.save()
        messages.success(request, "Bannissement modifié")
        return redirect("/users/")
    return form({'userform': ban}, 'users/user.html', request)

@login_required
def add_whitelist(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    whitelist_instance = Whitelist(user=user)
    whitelist = WhitelistForm(request.POST or None, instance=whitelist_instance)
    if whitelist.is_valid():
        whitelist.save()
        messages.success(request, "Accès à titre gracieux accordé")
        return redirect("/users/profil/" + userid)
    if is_whitelisted(user):
        messages.error(
            request,
            "Attention, cet utilisateur a deja un accès gracieux actif"
        )
    return form({'userform': whitelist}, 'users/user.html', request)

@login_required
def edit_whitelist(request, whitelistid):
    try:
        whitelist_instance = Whitelist.objects.get(pk=whitelistid)
    except Whitelist.DoesNotExist:
        messages.error(request, "Entrée inexistante")
        return redirect("/users/")
    whitelist = WhitelistForm(request.POST or None, instance=whitelist_instance)
    if whitelist.is_valid():
        whitelist.save()
        messages.success(request, "Whitelist modifiée")
        return redirect("/users/")
    return form({'userform': whitelist}, 'users/user.html', request)

@login_required
def add_school(request):
    school = SchoolForm(request.POST or None)
    if school.is_valid():
        school.save()
        messages.success(request, "L'établissement a été ajouté")
        return redirect("/users/index_school/")
    return form({'userform': school}, 'users/user.html', request)

@login_required
def edit_school(request, schoolid):
    try:
        school_instance = School.objects.get(pk=schoolid)
    except School.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/users/")
    school = SchoolForm(request.POST or None, instance=school_instance)
    if school.is_valid():
        school.save()
        messages.success(request, "Établissement modifié")
        return redirect("/users/index_school/")
    return form({'userform': school}, 'users/user.html', request)

@login_required
def del_school(request):
    school = DelSchoolForm(request.POST or None)
    if school.is_valid():
        school_dels = school.cleaned_data['schools']
        for school_del in school_dels:
            try:
                school_del.delete()
                messages.success(request, "L'établissement a été supprimé")
            except ProtectedError:
                messages.error(
                    request,
                    "L'établissement %s est affecté à au moins un user, \
                        vous ne pouvez pas le supprimer" % school_del)
        return redirect("/users/index_school/")
    return form({'userform': school}, 'users/user.html', request)

@login_required
def index(request):
    users_list = User.objects.order_by('pk')
    connexion = []
    for user in users_list:
        end = end_adhesion(user)
        access = has_access(user)
        if(end is not None):
            connexion.append([user, access, end])
        else:
            connexion.append([user, access, "Non adhérent"])
    return render(request, 'users/index.html', {'users_list': connexion})

@login_required
def index_ban(request):
    ban_list = Ban.objects.order_by('date_start')
    return render(request, 'users/index_ban.html', {'ban_list': ban_list})

@login_required
def index_white(request):
    white_list = Whitelist.objects.order_by('date_start')
    return render(
        request,
        'users/index_whitelist.html',
        {'white_list': white_list}
    )

@login_required
def index_school(request):
    school_list = School.objects.order_by('name')
    return render(request, 'users/index_schools.html', {'school_list':school_list})

@login_required
def profil(request, userid):
    try:
        users = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    machines = Interface.objects.filter(
        machine=Machine.objects.filter(user__pseudo=users)
    )
    factures = Facture.objects.filter(user__pseudo=users)
    bans = Ban.objects.filter(user__pseudo=users)
    whitelists = Whitelist.objects.filter(user__pseudo=users)
    end_bans = None
    end_whitelists = None
    if(is_ban(users)):
        end_bans = end_ban(users)
    if(is_whitelisted(users)):
        end_whitelists = end_whitelist(users)
    list_droits = Right.objects.filter(user=users)
    return render(
        request,
        'users/profil.html',
        {
            'user': users,
            'interfaces_list': machines,
            'facture_list': factures,
            'ban_list': bans,
            'white_list': whitelists,
            'end_ban': end_bans,
            'end_whitelist': end_whitelists,
            'end_adhesion': end_adhesion(users),
            'actif':has_access(users),
            'list_droits': list_droits
        }
    )

