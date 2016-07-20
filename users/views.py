# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz
# Gplv2
from django.shortcuts import render_to_response, get_object_or_404, render, redirect
from django.core.context_processors import csrf
from django.template import Context, RequestContext, loader
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Max, ProtectedError
from django.db import IntegrityError
from django.core.mail import send_mail
from django.utils import timezone
from django.core.urlresolvers import reverse

from users.models import User, Right, Ban, Whitelist, School, Request
from users.models import DelRightForm, BanForm, WhitelistForm, DelSchoolForm
from users.models import InfoForm, BaseInfoForm, StateForm, RightForm, SchoolForm
from cotisations.models import Facture
from machines.models import Machine, Interface
from users.forms import PassForm, ResetPasswordForm
from machines.views import unassign_ips, assign_ips

from re2o.login import hashNT
from re2o.settings import REQ_EXPIRE_STR, EMAIL_FROM, ASSO_NAME, ASSO_EMAIL, SITE_NAME

def archive(user):
    """ Archive un utilisateur """
    unassign_ips(user)
    return


def unarchive(user):
    """ Triger actions au desarchivage d'un user """
    assign_ips(user)
    return

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render_to_response(
        template,
        c,
        context_instance=RequestContext(request)
    )

def password_change_action(u_form, user, request, req=False):
    """ Fonction qui effectue le changeemnt de mdp bdd"""
    if u_form.cleaned_data['passwd1'] != u_form.cleaned_data['passwd2']:
        messages.error(request, "Les 2 mots de passe différent")
        return form({'userform': u_form}, 'users/user.html', request)
    user.set_password(u_form.cleaned_data['passwd1'])
    user.pwd_ntlm = hashNT(u_form.cleaned_data['passwd1'])
    user.save()
    messages.success(request, "Le mot de passe a changé")
    if req:
        req.delete()
        return redirect("/")
    return redirect("/users/profil/" + str(user.id))

def reset_passwd_mail(req, request):
    t = loader.get_template('users/email_passwd_request')
    c = Context({
      'name': str(req.user.name) + ' ' + str(req.user.surname),
      'asso': ASSO_NAME,
      'asso_mail': ASSO_EMAIL,
      'site_name': SITE_NAME,
      'url': request.build_absolute_uri(
       reverse('users:process', kwargs={'token': req.token})),
       'expire_in': REQ_EXPIRE_STR,
    })
    send_mail('Changement de mot de passe', t.render(c),
    EMAIL_FROM, [req.user.email], fail_silently=False)
    return

@login_required
@permission_required('cableur')
def new_user(request):
    user = InfoForm(request.POST or None)
    if user.is_valid():
        user = user.save(commit=False)
        user.save()
        req = Request()
        req.type = Request.PASSWD
        req.user = user
        req.save()
        reset_passwd_mail(req, request)
        messages.success(request, "L'utilisateur %s a été crée, un mail pour l'initialisation du mot de passe a été envoyé" % user.pseudo)
        redirect("/users/profil/" + user.id)
    return form({'userform': user}, 'users/user.html', request)

@login_required
def edit_info(request, userid):
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    if not request.user.has_perms(('cableur',)) and user != request.user:
        messages.error(request, "Vous ne pouvez pas modifier un autre user que vous sans droit cableur")
        return redirect("/users/profil/" + str(request.user.id))
    if not request.user.has_perms(('cableur',)):
        user = BaseInfoForm(request.POST or None, instance=user)
    else:
        user = InfoForm(request.POST or None, instance=user)
    if user.is_valid():
        user.save()
        messages.success(request, "L'user a bien été modifié")
        return redirect("/users/profil/" + userid)
    return form({'userform': user}, 'users/user.html', request)

@login_required
@permission_required('bureau')
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
    if not request.user.has_perms(('cableur',)) and user != request.user:
        messages.error(request, "Vous ne pouvez pas modifier un autre user que vous sans droit cableur")
        return redirect("/users/profil/" + str(request.user.id))
    if not request.user.has_perms(('bureau',)) and user != request.user and Right.objects.filter(user=user):
        messages.error(request, "Il faut les droits bureau pour modifier le mot de passe d'un membre actif")
        return redirect("/users/profil/" + str(request.user.id))
    u_form = PassForm(request.POST or None)
    if u_form.is_valid():
        return password_change_action(u_form, user, request)
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
@permission_required('bofh')
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
    if user.is_ban():
        messages.error(
            request,
            "Attention, cet utilisateur a deja un bannissement actif"
        )
    return form({'userform': ban}, 'users/user.html', request)

@login_required
@permission_required('bofh')
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
@permission_required('cableur')
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
@permission_required('cableur')
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
@permission_required('cableur')
def add_school(request):
    school = SchoolForm(request.POST or None)
    if school.is_valid():
        school.save()
        messages.success(request, "L'établissement a été ajouté")
        return redirect("/users/index_school/")
    return form({'userform': school}, 'users/user.html', request)

@login_required
@permission_required('cableur')
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
@permission_required('cableur')
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
@permission_required('cableur')
def index(request):
    users_list = User.objects.order_by('pk')
    return render(request, 'users/index.html', {'users_list': users_list})

@login_required
@permission_required('cableur')
def index_ban(request):
    ban_list = Ban.objects.order_by('date_start')
    return render(request, 'users/index_ban.html', {'ban_list': ban_list})

@login_required
@permission_required('cableur')
def index_white(request):
    white_list = Whitelist.objects.order_by('date_start')
    return render(
        request,
        'users/index_whitelist.html',
        {'white_list': white_list}
    )

@login_required
@permission_required('cableur')
def index_school(request):
    school_list = School.objects.order_by('name')
    return render(request, 'users/index_schools.html', {'school_list':school_list})

@login_required
def mon_profil(request):
    return redirect("/users/profil/" + str(request.user.id))

@login_required
def profil(request, userid):
    try:
        users = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    if not request.user.has_perms(('cableur',)) and users != request.user:
        messages.error(request, "Vous ne pouvez pas afficher un autre user que vous sans droit cableur")
        return redirect("/users/profil/" + str(request.user.id))
    machines = Machine.objects.filter(user__pseudo=users)
    factures = Facture.objects.filter(user__pseudo=users)
    bans = Ban.objects.filter(user__pseudo=users)
    whitelists = Whitelist.objects.filter(user__pseudo=users)
    list_droits = Right.objects.filter(user=users)
    return render(
        request,
        'users/profil.html',
        {
            'user': users,
            'machines_list': machines,
            'facture_list': factures,
            'ban_list': bans,
            'white_list': whitelists,
            'list_droits': list_droits,
        }
    )

def reset_password(request):
    userform = ResetPasswordForm(request.POST or None)
    if userform.is_valid():
        try:
            user = User.objects.get(pseudo=userform.cleaned_data['pseudo'],email=userform.cleaned_data['email'])
        except User.DoesNotExist:
            messages.error(request, "Cet utilisateur n'existe pas")
            return form({'userform': userform}, 'users/user.html', request)   
        req = Request()
        req.type = Request.PASSWD
        req.user = user
        req.save()
        reset_passwd_mail(req, request)
        messages.success(request, "Un mail pour l'initialisation du mot de passe a été envoyé")
        redirect("/") 
    return form({'userform': userform}, 'users/user.html', request)

def process(request, token):
    valid_reqs = Request.objects.filter(expires_at__gt=timezone.now())
    req = get_object_or_404(valid_reqs, token=token)

    if req.type == Request.PASSWD:
        return process_passwd(request, req)
    elif req.type == Request.EMAIL:
        return process_email(request, req=req)
    else:
        messages.error(request, "Entrée incorrecte, contactez un admin")
        redirect("/")

def process_passwd(request, req):
    u_form = PassForm(request.POST or None)
    user = req.user
    if u_form.is_valid():
        return password_change_action(u_form, user, request, req=req)
    return form({'userform': u_form}, 'users/user.html', request)
