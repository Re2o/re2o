# App de gestion des users pour re2o
# Goulven Kermarec, Gabriel Détraz
# Gplv2
from django.shortcuts import render_to_response, get_object_or_404, render, redirect
from django.core.context_processors import csrf
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

from reversion import revisions as reversion
from users.models import User, Right, Ban, Whitelist, School, ListRight, Request
from users.models import DelRightForm, BanForm, WhitelistForm, DelSchoolForm, DelListRightForm, NewListRightForm
from users.models import EditInfoForm, InfoForm, BaseInfoForm, StateForm, RightForm, SchoolForm, ListRightForm
from cotisations.models import Facture
from machines.models import Machine, Interface
from users.forms import PassForm, ResetPasswordForm
from machines.views import unassign_ips, assign_ips

from re2o.login import hashNT
from re2o.settings import REQ_EXPIRE_STR, EMAIL_FROM, ASSO_NAME, ASSO_EMAIL, SITE_NAME, PAGINATION_NUMBER

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
    with transaction.atomic(), reversion.create_revision():
        user.save()
        reversion.set_comment("Réinitialisation du mot de passe")
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
        with transaction.atomic(), reversion.create_revision():
            user.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        req = Request()
        req.type = Request.PASSWD
        req.user = user
        req.save()
        reset_passwd_mail(req, request)
        messages.success(request, "L'utilisateur %s a été crée, un mail pour l'initialisation du mot de passe a été envoyé" % user.pseudo)
        return redirect("/users/profil/" + str(user.id))
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
        user = EditInfoForm(request.POST or None, instance=user)
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
    try:
        user = User.objects.get(pk=userid)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur inexistant")
        return redirect("/users/")
    state = StateForm(request.POST or None, instance=user)
    if state.is_valid():
        if state.has_changed():
            if state.cleaned_data['state'] == User.STATE_ARCHIVE:
                archive(user)
            else:
                unarchive(user)
        with transaction.atomic(), reversion.create_revision():
            state.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in state.changed_data))
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
    user_right_list = DelRightForm(request.POST or None)
    if user_right_list.is_valid():
        right_del = user_right_list.cleaned_data['rights']
        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(request.user)
            reversion.set_comment("Retrait des droit %s" % ','.join(str(deleted_right) for deleted_right in right_del))
            right_del.delete()
        messages.success(request, "Droit retiré avec succès")
        return redirect("/users/")
    return form({'userform': user_right_list}, 'users/user.html', request)

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
        with transaction.atomic(), reversion.create_revision():
            ban.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
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
    if user.is_whitelisted():
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
@permission_required('cableur')
def index(request):
    users_list = User.objects.order_by('pk')
    paginator = Paginator(users_list, PAGINATION_NUMBER)
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
    ban_list = Ban.objects.order_by('date_start').reverse()
    paginator = Paginator(ban_list, PAGINATION_NUMBER)
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
@permission_required('cableur')
def index_listright(request):
    listright_list = ListRight.objects.order_by('listright')
    return render(request, 'users/index_listright.html', {'listright_list':listright_list})

@login_required
def history(request, object, id):
    if object == 'user':
        try:
             object_instance = User.objects.get(pk=id)
        except User.DoesNotExist:
             messages.error(request, "Utilisateur inexistant")
             return redirect("/users/")
        if not request.user.has_perms(('cableur',)) and object_instance != request.user:
             messages.error(request, "Vous ne pouvez pas afficher l'historique d'un autre user que vous sans droit cableur")
             return redirect("/users/profil/" + str(request.user.id))
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
    reversions = reversion.get_for_object(object_instance)
    paginator = Paginator(reversions, PAGINATION_NUMBER)
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
