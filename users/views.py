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

# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz, Lemesle Augustin
# Gplv2
from django.shortcuts import get_object_or_404, render, redirect
from django.template.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import Context, RequestContext, loader
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Max, ProtectedError
from django.db import IntegrityError
from django.core.mail import send_mail
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db import transaction

from reversion.models import Version
from reversion import revisions as reversion
from users.models import User, Right, Ban, Whitelist, School, ListRight, Request, ServiceUser
from users.forms import DelRightForm, BanForm, WhitelistForm, DelSchoolForm, DelListRightForm, NewListRightForm
from users.forms import EditInfoForm, InfoForm, BaseInfoForm, StateForm, RightForm, SchoolForm, EditServiceUserForm, ServiceUserForm, ListRightForm
from cotisations.models import Facture
from machines.models import Machine, Interface
from users.forms import MassArchiveForm, PassForm, ResetPasswordForm
from preferences.models import OptionalUser, AssoOption, GeneralOption

from re2o.login import hashNT
from re2o.settings import REQ_EXPIRE_STR, EMAIL_FROM, SITE_NAME


def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render(request, template, c)

def password_change_action(u_form, user, request, req=False):
    """ Fonction qui effectue le changeemnt de mdp bdd"""
    if u_form.cleaned_data['passwd1'] != u_form.cleaned_data['passwd2']:
        messages.error(request, "Les 2 mots de passe différent")
        return form({'userform': u_form}, 'users/user.html', request)
    user.set_password(u_form.cleaned_data['passwd1'])
    user.pwd_ntlm = hashNT(u_form.cleaned_data['passwd1'])
    with transaction.atomic(), reversion.create_revision():
        user.save()
        reversion.set_comment("Réinitialisation du mot de passe")
    messages.success(request, "Le mot de passe a changé")
    if req:
        req.delete()
        return redirect("/")
    return redirect("/users/profil/" + str(user.id))

def reset_passwd_mail(req, request):
    """ Prend en argument un request, envoie un mail de réinitialisation de mot de pass """
    t = loader.get_template('users/email_passwd_request')
    options, created = AssoOption.objects.get_or_create() 
    c = {
      'name': str(req.user.name) + ' ' + str(req.user.surname),
      'asso': options.name,
      'asso_mail': options.contact,
      'site_name': SITE_NAME,
      'url': request.build_absolute_uri(
       reverse('users:process', kwargs={'token': req.token})),
       'expire_in': REQ_EXPIRE_STR,
    }
    send_mail('Changement de mot de passe du Rézo Metz / Password renewal for Rézo Metz', t.render(c),
    EMAIL_FROM, [req.user.email], fail_silently=False)
    return

def notif_ban(ban):
    """ Prend en argument un objet ban, envoie un mail de notification """
    t = loader.get_template('users/email_ban_notif')
    c = Context({
      'name': str(ban.user.name) + ' ' + str(ban.user.surname),
      'raison': ban.raison,
      'date_end': ban.date_end,
    })
    send_mail('Deconnexion disciplinaire', t.render(c),
    EMAIL_FROM, [ban.user.email], fail_silently=False)
    return

def notif_inscription(user):
    """ Prend en argument un objet user, envoie un mail de bienvenue """
    t = loader.get_template('users/email_welcome')
    options, created = AssoOption.objects.get_or_create()
    c = Context({
      'nom': str(user.name) + ' ' + str(user.surname),
      'asso_name': options.name,
      'asso_email': options.contact,
      'pseudo':user.pseudo,
    })
    send_mail('Bienvenue au Rézo / Welcome to Rézo Metz', '',
    EMAIL_FROM, [user.email], html_message=t.render(c))
    return


@login_required
@permission_required('cableur')
def new_user(request):
    """ Vue de création d'un nouvel utilisateur, envoie un mail pour le mot de passe"""
    user = InfoForm(request.POST or None)
    if user.is_valid():
        user = user.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            user.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        req = Request()
        req.type = Request.PASSWD
        req.user = user
        req.save()
        reset_passwd_mail(req, request)
        notif_inscription(user)
        messages.success(request, "L'utilisateur %s a été crée, un mail pour l'initialisation du mot de passe a été envoyé" % user.pseudo)
        return redirect("/users/profil/" + str(user.id))
    return form({'userform': user}, 'users/user.html', request)

@login_required
def edit_info(request, userid):
    """ Edite un utilisateur à partir de son id, 
    si l'id est différent de request.user, vérifie la possession du droit cableur """
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
        with transaction.atomic(), reversion.create_revision():
            user.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in user.changed_data))
        messages.success(request, "L'user a bien été modifié")
        return redirect("/users/profil/" + userid)
    return form({'userform': user}, 'users/user.html', request)

@login_required
@permission_required('bureau')
def state(request, userid):
    """ Changer l'etat actif/desactivé/archivé d'un user, need droit bureau """
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    state = StateForm(request.POST or None, instance=user)
    if state.is_valid():
        with transaction.atomic(), reversion.create_revision():
            if state.cleaned_data['state'] == User.STATE_ARCHIVE:
                user.archive()
            elif state.cleaned_data['state'] == User.STATE_ACTIVE:
                user.unarchive()
            elif state.cleaned_data['state'] == User.STATE_DISABLED:
                user.state = User.STATE_DISABLED
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in state.changed_data))
            user.save()
        messages.success(request, "Etat changé avec succès")
        return redirect("/users/profil/" + userid)
    return form({'userform': state}, 'users/user.html', request)

@login_required
def password(request, userid):
    """ Reinitialisation d'un mot de passe à partir de l'userid,
    pour self par défaut, pour tous sans droit si droit cableur,
    pour tous si droit bureau """
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
@permission_required('infra')
def new_serviceuser(request):
    """ Vue de création d'un nouvel utilisateur service"""
    user = ServiceUserForm(request.POST or None)
    if user.is_valid():
        user_object = user.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            user_object.set_password(user.cleaned_data['password'])
            user_object.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "L'utilisateur %s a été crée" % user_object.pseudo)
        return redirect("/users/index_serviceusers/")
    return form({'userform': user}, 'users/user.html', request)

@login_required
@permission_required('infra')
def edit_serviceuser(request, userid):
    """ Edite un utilisateur à partir de son id, 
    si l'id est différent de request.user, vérifie la possession du droit cableur """
    try:
        user = ServiceUser.objects.get(pk=userid)
    except ServiceUser.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    user = EditServiceUserForm(request.POST or None, instance=user)
    if user.is_valid():
        user_object = user.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            if user.cleaned_data['password']:
                user_object.set_password(user.cleaned_data['password'])
            user_object.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in user.changed_data))
        messages.success(request, "L'user a bien été modifié")
        return redirect("/users/index_serviceusers")
    return form({'userform': user}, 'users/user.html', request)

@login_required
@permission_required('infra')
def del_serviceuser(request, userid):
    try:
        user = ServiceUser.objects.get(pk=userid)
    except ServiceUser.DoesNotExist:
        messages.error(request, u"Utilisateur inexistant" )
        return redirect("/users/")
    if request.method == "POST":
        with transaction.atomic(), reversion.create_revision():
            user.delete()
            reversion.set_user(request.user)
        messages.success(request, "L'user a été détruite")
        return redirect("/users/index_serviceusers/")
    return form({'objet': user, 'objet_name': 'serviceuser'}, 'users/delete.html', request)

@login_required
@permission_required('bureau')
def add_right(request, userid):
    """ Ajout d'un droit à un user, need droit bureau """
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
            with transaction.atomic(), reversion.create_revision():
                reversion.set_user(request.user)
                reversion.set_comment("Ajout du droit %s" % right.right)
                right.save()
            messages.success(request, "Droit ajouté")
        except IntegrityError:
            pass
        return redirect("/users/profil/" + userid)
    return form({'userform': right}, 'users/user.html', request)

@login_required
@permission_required('bureau')
def del_right(request):
    """ Supprimer un droit à un user, need droit bureau """
    user_right_list = dict()
    for right in ListRight.objects.all():
        user_right_list[right]= DelRightForm(right, request.POST or None)
    for keys, right_item in user_right_list.items():
        if right_item.is_valid():
            right_del = right_item.cleaned_data['rights']
            with transaction.atomic(), reversion.create_revision():
                reversion.set_user(request.user)
                reversion.set_comment("Retrait des droit %s" % ','.join(str(deleted_right) for deleted_right in right_del))
                right_del.delete()
            messages.success(request, "Droit retiré avec succès")
            return redirect("/users/")
    return form({'userform': user_right_list}, 'users/del_right.html', request)

@login_required
@permission_required('bofh')
def add_ban(request, userid):
    """ Ajouter un banissement, nécessite au moins le droit bofh (a fortiori bureau)
    Syntaxe : JJ/MM/AAAA , heure optionnelle, prend effet immédiatement"""
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    ban_instance = Ban(user=user)
    ban = BanForm(request.POST or None, instance=ban_instance)
    if ban.is_valid():
        with transaction.atomic(), reversion.create_revision():
            ban_object = ban.save()
            notif_ban(ban_object)
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Bannissement ajouté")
        return redirect("/users/profil/" + userid)
    if user.is_ban:
        messages.error(
            request,
            "Attention, cet utilisateur a deja un bannissement actif"
        )
    return form({'userform': ban}, 'users/user.html', request)

@login_required
@permission_required('bofh')
def edit_ban(request, banid):
    """ Editer un bannissement, nécessite au moins le droit bofh (a fortiori bureau)
    Syntaxe : JJ/MM/AAAA , heure optionnelle, prend effet immédiatement"""
    try:
        ban_instance = Ban.objects.get(pk=banid)
    except Ban.DoesNotExist:
        messages.error(request, "Entrée inexistante")
        return redirect("/users/")
    ban = BanForm(request.POST or None, instance=ban_instance)
    if ban.is_valid():
        with transaction.atomic(), reversion.create_revision():
            ban.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in ban.changed_data))
        messages.success(request, "Bannissement modifié")
        return redirect("/users/")
    return form({'userform': ban}, 'users/user.html', request)

@login_required
@permission_required('cableur')
def add_whitelist(request, userid):
    """ Accorder un accès gracieux, temporaire ou permanent. Need droit cableur
    Syntaxe : JJ/MM/AAAA , heure optionnelle, prend effet immédiatement, raison obligatoire"""
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    whitelist_instance = Whitelist(user=user)
    whitelist = WhitelistForm(request.POST or None, instance=whitelist_instance)
    if whitelist.is_valid():
        with transaction.atomic(), reversion.create_revision():
            whitelist.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Accès à titre gracieux accordé")
        return redirect("/users/profil/" + userid)
    if user.is_whitelisted:
        messages.error(
            request,
            "Attention, cet utilisateur a deja un accès gracieux actif"
        )
    return form({'userform': whitelist}, 'users/user.html', request)

@login_required
@permission_required('cableur')
def edit_whitelist(request, whitelistid):
    """ Editer un accès gracieux, temporaire ou permanent. Need droit cableur
    Syntaxe : JJ/MM/AAAA , heure optionnelle, prend effet immédiatement, raison obligatoire"""
    try:
        whitelist_instance = Whitelist.objects.get(pk=whitelistid)
    except Whitelist.DoesNotExist:
        messages.error(request, "Entrée inexistante")
        return redirect("/users/")
    whitelist = WhitelistForm(request.POST or None, instance=whitelist_instance)
    if whitelist.is_valid():
        with transaction.atomic(), reversion.create_revision():
            whitelist.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in whitelist.changed_data))
        messages.success(request, "Whitelist modifiée")
        return redirect("/users/")
    return form({'userform': whitelist}, 'users/user.html', request)

@login_required
@permission_required('cableur')
def add_school(request):
    """ Ajouter un établissement d'enseignement à la base de donnée, need cableur"""
    school = SchoolForm(request.POST or None)
    if school.is_valid():
        with transaction.atomic(), reversion.create_revision():
            school.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "L'établissement a été ajouté")
        return redirect("/users/index_school/")
    return form({'userform': school}, 'users/user.html', request)

@login_required
@permission_required('cableur')
def edit_school(request, schoolid):
    """ Editer un établissement d'enseignement à partir du schoolid dans la base de donnée, need cableur"""
    try:
        school_instance = School.objects.get(pk=schoolid)
    except School.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/users/")
    school = SchoolForm(request.POST or None, instance=school_instance)
    if school.is_valid():
        with transaction.atomic(), reversion.create_revision():
            school.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in school.changed_data))
        messages.success(request, "Établissement modifié")
        return redirect("/users/index_school/")
    return form({'userform': school}, 'users/user.html', request)

@login_required
@permission_required('cableur')
def del_school(request):
    """ Supprimer un établissement d'enseignement à la base de donnée, need cableur
    Objet protégé, possible seulement si aucun user n'est affecté à l'établissement """
    school = DelSchoolForm(request.POST or None)
    if school.is_valid():
        school_dels = school.cleaned_data['schools']
        for school_del in school_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    school_del.delete()
                    reversion.set_comment("Destruction")
                messages.success(request, "L'établissement a été supprimé")
            except ProtectedError:
                messages.error(
                    request,
                    "L'établissement %s est affecté à au moins un user, \
                        vous ne pouvez pas le supprimer" % school_del)
        return redirect("/users/index_school/")
    return form({'userform': school}, 'users/user.html', request)

@login_required
@permission_required('bureau')
def add_listright(request):
    """ Ajouter un droit/groupe, nécessite droit bureau.
    Obligation de fournir un gid pour la synchro ldap, unique """
    listright = NewListRightForm(request.POST or None)
    if listright.is_valid():
        with transaction.atomic(), reversion.create_revision():
            listright.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Le droit/groupe a été ajouté")
        return redirect("/users/index_listright/")
    return form({'userform': listright}, 'users/user.html', request)

@login_required
@permission_required('bureau')
def edit_listright(request, listrightid):
    """ Editer un groupe/droit, necessite droit bureau, à partir du listright id """
    try:
        listright_instance = ListRight.objects.get(pk=listrightid)
    except ListRight.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/users/")
    listright = ListRightForm(request.POST or None, instance=listright_instance)
    if listright.is_valid():
        with transaction.atomic(), reversion.create_revision():
            listright.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in listright.changed_data))
        messages.success(request, "Droit modifié")
        return redirect("/users/index_listright/")
    return form({'userform': listright}, 'users/user.html', request)

@login_required
@permission_required('bureau')
def del_listright(request):
    """ Supprimer un ou plusieurs groupe, possible si il est vide, need droit bureau """
    listright = DelListRightForm(request.POST or None)
    if listright.is_valid():
        listright_dels = listright.cleaned_data['listrights']
        for listright_del in listright_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    listright_del.delete()
                    reversion.set_comment("Destruction")
                messages.success(request, "Le droit/groupe a été supprimé")
            except ProtectedError:
                messages.error(
                    request,
                    "L'établissement %s est affecté à au moins un user, \
                        vous ne pouvez pas le supprimer" % listright_del)
        return redirect("/users/index_listright/")
    return form({'userform': listright}, 'users/user.html', request)

@login_required
@permission_required('bureau')
def mass_archive(request):
    """ Permet l'archivage massif"""
    to_archive_date = MassArchiveForm(request.POST or None)
    to_archive_list = []
    if to_archive_date.is_valid():
        date = to_archive_date.cleaned_data['date']
        to_archive_list = [user for user in User.objects.exclude(state=User.STATE_ARCHIVE) if not user.end_access() or user.end_access() < date]
        if "valider" in request.POST:
            for user in to_archive_list:
                with transaction.atomic(), reversion.create_revision():
                    user.archive()
                    user.save()
                    reversion.set_user(request.user)
                    reversion.set_comment("Archivage")
            messages.success(request, "%s users ont été archivés" % len(to_archive_list))
            return redirect("/users/")        
    return form({'userform': to_archive_date, 'to_archive_list': to_archive_list}, 'users/mass_archive.html', request)

@login_required
@permission_required('cableur')
def index(request):
    """ Affiche l'ensemble des users, need droit cableur """
    options, created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    users_list = User.objects.select_related('room').order_by('state', 'name')
    paginator = Paginator(users_list, pagination_number)
    page = request.GET.get('page')
    try:
        users_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users_list = paginator.page(paginator.num_pages)
    return render(request, 'users/index.html', {'users_list': users_list})

@login_required
@permission_required('cableur')
def index_ban(request):
    """ Affiche l'ensemble des ban, need droit cableur """
    options, created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    ban_list = Ban.objects.order_by('date_start').select_related('user').reverse()
    paginator = Paginator(ban_list, pagination_number)
    page = request.GET.get('page')
    try:
        ban_list = paginator.page(page)
    except PageNotAnInteger:
        # If page isn't an integer, deliver first page
        ban_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results. 
        ban_list = paginator.page(paginator.num_pages) 
    return render(request, 'users/index_ban.html', {'ban_list': ban_list})

@login_required
@permission_required('cableur')
def index_white(request):
    """ Affiche l'ensemble des whitelist, need droit cableur """
    white_list = Whitelist.objects.select_related('user').order_by('date_start')
    return render(
        request,
        'users/index_whitelist.html',
        {'white_list': white_list}
    )

@login_required
@permission_required('cableur')
def index_school(request):
    """ Affiche l'ensemble des établissement, need droit cableur """
    school_list = School.objects.order_by('name')
    return render(request, 'users/index_schools.html', {'school_list':school_list})

@login_required
@permission_required('cableur')
def index_listright(request):
    """ Affiche l'ensemble des droits , need droit cableur """
    listright_list = ListRight.objects.order_by('listright')
    return render(request, 'users/index_listright.html', {'listright_list':listright_list})

@login_required
@permission_required('cableur')
def index_serviceusers(request):
    """ Affiche les users de services (pour les accès ldap)"""
    serviceusers_list = ServiceUser.objects.order_by('pseudo')
    return render(request, 'users/index_serviceusers.html', {'serviceusers_list':serviceusers_list})

@login_required
def history(request, object, id):
    """ Affichage de l'historique : (acl, argument)
    user : self or cableur, userid,
    ban : self or cableur, banid,
    whitelist : self or cableur, whitelistid,
    school : cableur, schoolid,
    listright : cableur, listrightid """
    if object == 'user':
        try:
             object_instance = User.objects.get(pk=id)
        except User.DoesNotExist:
             messages.error(request, "Utilisateur inexistant")
             return redirect("/users/")
        if not request.user.has_perms(('cableur',)) and object_instance != request.user:
             messages.error(request, "Vous ne pouvez pas afficher l'historique d'un autre user que vous sans droit cableur")
             return redirect("/users/profil/" + str(request.user.id))
    elif object == 'serviceuser' and request.user.has_perms(('cableur',)):
        try:
             object_instance = ServiceUser.objects.get(pk=id)
        except ServiceUser.DoesNotExist:
             messages.error(request, "User service inexistant")
             return redirect("/users/")
    elif object == 'ban':
        try:
             object_instance = Ban.objects.get(pk=id)
        except Ban.DoesNotExist:
             messages.error(request, "Bannissement inexistant")
             return redirect("/users/")
        if not request.user.has_perms(('cableur',)) and object_instance.user != request.user:
             messages.error(request, "Vous ne pouvez pas afficher les bans d'un autre user que vous sans droit cableur")
             return redirect("/users/profil/" + str(request.user.id))
    elif object == 'whitelist':
        try:
             object_instance = Whitelist.objects.get(pk=id)
        except Whiltelist.DoesNotExist:
             messages.error(request, "Whitelist inexistant")
             return redirect("/users/")
        if not request.user.has_perms(('cableur',)) and object_instance.user != request.user:
             messages.error(request, "Vous ne pouvez pas afficher les whitelist d'un autre user que vous sans droit cableur")
             return redirect("/users/profil/" + str(request.user.id))
    elif object == 'school' and request.user.has_perms(('cableur',)):
        try:
             object_instance = School.objects.get(pk=id)
        except School.DoesNotExist:
             messages.error(request, "Ecole inexistante")
             return redirect("/users/")
    elif object == 'listright' and request.user.has_perms(('cableur',)):
        try:
             object_instance = ListRight.objects.get(pk=id)
        except ListRight.DoesNotExist:
             messages.error(request, "Droit inexistant")
             return redirect("/users/")
    else:
        messages.error(request, "Objet  inconnu")
        return redirect("/users/")
    options, created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    reversions = Version.objects.get_for_object(object_instance)
    paginator = Paginator(reversions, pagination_number)
    page = request.GET.get('page')
    try:
        reversions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reversions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reversions = paginator.page(paginator.num_pages)
    return render(request, 're2o/history.html', {'reversions': reversions, 'object': object_instance})


@login_required
def mon_profil(request):
    """ Lien vers profil, renvoie request.id à la fonction """
    return redirect("/users/profil/" + str(request.user.id))

@login_required
def profil(request, userid):
    """ Affiche un profil, self or cableur, prend un userid en argument """
    try:
        users = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    if not request.user.has_perms(('cableur',)) and users != request.user:
        messages.error(request, "Vous ne pouvez pas afficher un autre user que vous sans droit cableur")
        return redirect("/users/profil/" + str(request.user.id))
    machines = Machine.objects.filter(user__pseudo=users).select_related('user').prefetch_related('interface_set__domain__extension').prefetch_related('interface_set__ipv4__ip_type__extension').prefetch_related('interface_set__type').prefetch_related('interface_set__domain__related_domain__extension')
    factures = Facture.objects.filter(user__pseudo=users)
    bans = Ban.objects.filter(user__pseudo=users)
    whitelists = Whitelist.objects.filter(user__pseudo=users)
    list_droits = Right.objects.filter(user=users)
    options, created = OptionalUser.objects.get_or_create()
    user_solde = options.user_solde
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
            'user_solde': user_solde,
        }
    )

def reset_password(request):
    """ Reintialisation du mot de passe si mdp oublié """
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
