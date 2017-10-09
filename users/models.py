# -*- mode: python; coding: utf-8 -*-
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

from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django import forms
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.template import Context, RequestContext, loader
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

from reversion import revisions as reversion
from django.db import transaction

import ldapdb.models
import ldapdb.models.fields

from re2o.settings import RIGHTS_LINK, LDAP, GID_RANGES,UID_RANGES
import re, uuid
import datetime
from re2o.login import hashNT

from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator
from topologie.models import Room
from cotisations.models import Cotisation, Facture, Paiement, Vente
from machines.models import Domain, Interface, MachineType, Machine, Nas, MachineType, Extension, regen
from preferences.models import GeneralOption, AssoOption, OptionalUser, OptionalMachine, MailMessageOption

now = timezone.now()


#### Utilitaires généraux

def remove_user_room(room):
    """ Déménage de force l'ancien locataire de la chambre """
    try:
        user = User.objects.get(room=room)
    except User.DoesNotExist:
        return
    user.room = None
    user.save()


def linux_user_check(login):
    """ Validation du pseudo pour respecter les contraintes unix"""
    UNIX_LOGIN_PATTERN = re.compile("^[a-zA-Z0-9-]*[$]?$")
    return UNIX_LOGIN_PATTERN.match(login)


def linux_user_validator(login):
    """ Retourne une erreur de validation si le login ne respecte 
    pas les contraintes unix (maj, min, chiffres ou tiret)"""
    if not linux_user_check(login):
        raise forms.ValidationError(
                ", ce pseudo ('%(label)s') contient des carractères interdits",
                params={'label': login},
        )

def get_fresh_user_uid():
    """ Renvoie le plus petit uid non pris. Fonction très paresseuse """
    uids = list(range(int(min(UID_RANGES['users'])),int(max(UID_RANGES['users']))))
    try:
        used_uids = list(User.objects.values_list('uid_number', flat=True))
    except:
        used_uids = []
    free_uids = [ id for id in uids if id not in used_uids]
    return min(free_uids)

def get_fresh_gid():
    """ Renvoie le plus petit gid libre  """
    gids = list(range(int(min(GID_RANGES['posix'])),int(max(GID_RANGES['posix']))))
    used_gids = list(ListRight.objects.values_list('gid', flat=True))
    free_gids = [ id for id in gids if id not in used_gids]
    return min(free_gids)

def get_admin_right():
    """ Renvoie l'instance droit admin. La crée si elle n'existe pas 
    Lui attribue un gid libre"""
    try:
        admin_right = ListRight.objects.get(listright="admin")
    except ListRight.DoesNotExist:
        admin_right = ListRight(listright="admin")
        admin_right.gid = get_fresh_gid()
        admin_right.save()
    return admin_right

def all_adherent(search_time=now):
    """ Fonction renvoyant tous les users adherents. Optimisee pour n'est qu'une seule requete sql
    Inspecte les factures de l'user et ses cotisation, regarde si elles sont posterieur à now (end_time)"""
    return User.objects.filter(facture__in=Facture.objects.filter(vente__in=Vente.objects.filter(cotisation__in=Cotisation.objects.filter(vente__in=Vente.objects.filter(facture__in=Facture.objects.all().exclude(valid=False))).filter(date_end__gt=search_time)))).distinct()

def all_baned(search_time=now):
    """ Fonction renvoyant tous les users bannis """
    return User.objects.filter(ban__in=Ban.objects.filter(date_end__gt=search_time)).distinct() 

def all_whitelisted(search_time=now):
    """ Fonction renvoyant tous les users whitelistes """
    return User.objects.filter(whitelist__in=Whitelist.objects.filter(date_end__gt=search_time)).distinct()

def all_has_access(search_time=now):
    """  Renvoie tous les users beneficiant d'une connexion : user adherent ou whiteliste et non banni """
    return User.objects.filter(Q(state=User.STATE_ACTIVE) & ~Q(ban__in=Ban.objects.filter(date_end__gt=timezone.now())) & (Q(whitelist__in=Whitelist.objects.filter(date_end__gt=timezone.now())) | Q(facture__in=Facture.objects.filter(vente__in=Vente.objects.filter(cotisation__in=Cotisation.objects.filter(vente__in=Vente.objects.filter(facture__in=Facture.objects.all().exclude(valid=False))).filter(date_end__gt=search_time)))))).distinct()

class UserManager(BaseUserManager):
    def _create_user(self, pseudo, name, surname, email, password=None, su=False):
        if not pseudo:
            raise ValueError('Users must have an username')

        if not linux_user_check(pseudo):
            raise ValueError('Username shall only contain [a-z0-9-]')

        user = self.model(
            pseudo=pseudo,
            name=name,
            surname=surname,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        if su:
            user.make_admin()
        return user

    def create_user(self, pseudo, name, surname, email, password=None):
        """
        Creates and saves a User with the given pseudo, name, surname, email,
        and password.
        """
        return self._create_user(pseudo, name, surname, email, password, False)

    def create_superuser(self, pseudo, name, surname, email, password):
        """
        Creates and saves a superuser with the given pseudo, name, surname,
        email, and password.
        """
        return self._create_user(pseudo, name, surname, email, password, True)


class User(AbstractBaseUser):
    """ Definition de l'utilisateur de base.
    Champs principaux : name, surnname, pseudo, email, room, password
    Herite du django BaseUser et du système d'auth django"""
    PRETTY_NAME = "Utilisateurs"
    STATE_ACTIVE = 0
    STATE_DISABLED = 1
    STATE_ARCHIVE = 2
    STATES = (
            (0, 'STATE_ACTIVE'),
            (1, 'STATE_DISABLED'),
            (2, 'STATE_ARCHIVE'),
            )

    def auto_uid():
        return get_fresh_user_uid()

    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    pseudo = models.CharField(max_length=32, unique=True, help_text="Doit contenir uniquement des lettres, chiffres, ou tirets", validators=[linux_user_validator])
    email = models.EmailField()
    school = models.ForeignKey('School', on_delete=models.PROTECT, null=True, blank=True)
    shell = models.ForeignKey('ListShell', on_delete=models.PROTECT, null=True, blank=True)
    comment = models.CharField(help_text="Commentaire, promo", max_length=255, blank=True)
    room = models.OneToOneField('topologie.Room', on_delete=models.PROTECT, blank=True, null=True)
    pwd_ntlm = models.CharField(max_length=255)
    state = models.IntegerField(choices=STATES, default=STATE_ACTIVE)
    registered = models.DateTimeField(auto_now_add=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    uid_number = models.IntegerField(default=auto_uid, unique=True)
    rezo_rez_uid =  models.IntegerField(unique=True, blank=True, null=True)

    USERNAME_FIELD = 'pseudo'
    REQUIRED_FIELDS = ['name', 'surname', 'email']

    objects = UserManager()

    @property
    def is_active(self):
        """ Renvoie si l'user est à l'état actif"""
        return self.state == self.STATE_ACTIVE

    @property
    def is_staff(self):
        """ Fonction de base django, renvoie si l'user est admin"""
        return self.is_admin

    @property
    def is_admin(self):
        """ Renvoie si l'user est admin"""
        try:
            Right.objects.get(user=self, right__listright='admin')
        except Right.DoesNotExist:
            return False
        return True

    @is_admin.setter
    def is_admin(self, value):
        """ Change la valeur de admin à true ou false suivant la valeur de value"""
        if value and not self.is_admin:
            self.make_admin()
        elif not value and self.is_admin:
            self.un_admin()

    def get_full_name(self):
        """ Renvoie le nom complet de l'user formaté nom/prénom"""
        return '%s %s' % (self.name, self.surname)

    def get_short_name(self):
        """ Renvoie seulement le nom"""
        return self.name

    def has_perms(self, perms, obj=None):
        """ Renvoie true si l'user dispose de la permission.
        Prend en argument une liste de permissions.
        TODO : Arranger cette fonction"""
        for perm in perms:
            if perm in RIGHTS_LINK:
                query = Q()
                for right in RIGHTS_LINK[perm]:
                    query = query | Q(right__listright=right)
                if Right.objects.filter(Q(user=self) & query):
                    return True 
            try:
                Right.objects.get(user=self, right__listright=perm)
            except Right.DoesNotExist:
                return False
        return True

    def has_perm(self, perm, obj=None):
        return True


    def has_right(self, right):
        """ Renvoie si un user a un right donné. Crée le right si il n'existe pas"""
        try:
            list_right = ListRight.objects.get(listright=right)
        except:
            list_right = ListRight(listright=right, gid=get_fresh_gid())
            list_right.save()
        return Right.objects.filter(user=self).filter(right=list_right).exists()

    @cached_property
    def is_bureau(self):
        """ True si user a les droits bureau """
        return self.has_right('bureau')

    @cached_property
    def is_bofh(self):
        """ True si l'user a les droits bofh"""
        return self.has_right('bofh')

    @cached_property
    def is_cableur(self):
        """ True si l'user a les droits cableur 
        (également true si bureau, infra  ou bofh)"""
        return self.has_right('cableur') or self.has_right('bureau') or self.has_right('infra') or self.has_right('bofh')

    @cached_property
    def is_trez(self):
        """ Renvoie true si droits trésorier pour l'user"""
        return self.has_right('tresorier')

    @cached_property
    def is_infra(self):
        """ True si a les droits infra"""
        return self.has_right('infra')

    def end_adhesion(self):
        """ Renvoie la date de fin d'adhésion d'un user. Examine les objets
        cotisation"""
        date_max = Cotisation.objects.filter(vente__in=Vente.objects.filter(facture__in=Facture.objects.filter(user=self).exclude(valid=False))).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    def is_adherent(self):
        """ Renvoie True si l'user est adhérent : si self.end_adhesion()>now"""
        end = self.end_adhesion()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    @cached_property
    def end_ban(self):
        """ Renvoie la date de fin de ban d'un user, False sinon """
        date_max = Ban.objects.filter(user=self).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    @cached_property
    def end_whitelist(self):
        """ Renvoie la date de fin de whitelist d'un user, False sinon """
        date_max = Whitelist.objects.filter(user=self).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    @cached_property
    def is_ban(self):
        """ Renvoie si un user est banni ou non """
        end = self.end_ban
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    @cached_property
    def is_whitelisted(self):
        """ Renvoie si un user est whitelisté ou non """
        end = self.end_whitelist
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    def has_access(self):
        """ Renvoie si un utilisateur a accès à internet """
        return self.state == User.STATE_ACTIVE \
            and not self.is_ban and (self.is_adherent() or self.is_whitelisted)

    def end_access(self):
        """ Renvoie la date de fin normale d'accès (adhésion ou whiteliste)"""
        if not self.end_adhesion():
            if not self.end_whitelist:
                return None
            else:
                return self.end_whitelist
        else:
            if not self.end_whitelist:
                return self.end_adhesion()
            else:        
                return max(self.end_adhesion(), self.end_whitelist)

    @cached_property
    def solde(self):
        """ Renvoie le solde d'un user. Vérifie que l'option solde est activé, retourne 0 sinon.
        Somme les crédits de solde et retire les débit payés par solde"""
        options, created = OptionalUser.objects.get_or_create()
        user_solde = options.user_solde
        if user_solde:
            solde_object, created=Paiement.objects.get_or_create(moyen='Solde')
            somme_debit = Vente.objects.filter(facture__in=Facture.objects.filter(user=self, paiement=solde_object)).aggregate(total=models.Sum(models.F('prix')*models.F('number'), output_field=models.FloatField()))['total'] or 0
            somme_credit =Vente.objects.filter(facture__in=Facture.objects.filter(user=self), name="solde").aggregate(total=models.Sum(models.F('prix')*models.F('number'), output_field=models.FloatField()))['total'] or 0
            return somme_credit - somme_debit
        else:
            return 0

    def user_interfaces(self, active=True):
        """ Renvoie toutes les interfaces dont les machines appartiennent à self
        Par defaut ne prend que les interfaces actives"""
        return Interface.objects.filter(machine__in=Machine.objects.filter(user=self, active=active)).select_related('domain__extension')

    def assign_ips(self):
        """ Assign une ipv4 aux machines d'un user """
        interfaces = self.user_interfaces()
        for interface in interfaces:
            if not interface.ipv4:
                with transaction.atomic(), reversion.create_revision():
                    interface.assign_ipv4()
                    reversion.set_comment("Assignation ipv4")
                    interface.save()

    def unassign_ips(self):
        """ Désassigne les ipv4 aux machines de l'user"""
        interfaces = self.user_interfaces()
        for interface in interfaces:
            with transaction.atomic(), reversion.create_revision():
                interface.unassign_ipv4()
                reversion.set_comment("Désassignation ipv4")
                interface.save()

    def archive(self):
        """ Archive l'user : appelle unassign_ips() puis passe state à ARCHIVE"""
        self.unassign_ips()
        self.state = User.STATE_ARCHIVE 

    def unarchive(self):
        """ Désarchive l'user : réassigne ses ip et le passe en state ACTIVE"""
        self.assign_ips()
        self.state = User.STATE_ACTIVE

    def has_module_perms(self, app_label):
        # Simplest version again
        return True

    def make_admin(self):
        """ Make User admin """
        user_admin_right = Right(user=self, right=get_admin_right())
        user_admin_right.save()

    def un_admin(self):
        try:
            user_right = Right.objects.get(user=self,right=get_admin_right())
        except Right.DoesNotExist:
            return
        user_right.delete()

    def ldap_sync(self, base=True, access_refresh=True, mac_refresh=True):
        """ Synchronisation du ldap. Synchronise dans le ldap les attributs de self
        Options : base : synchronise tous les attributs de base - nom, prenom, mail, password, shell, home
        access_refresh : synchronise le dialup_access notant si l'user a accès aux services
        mac_refresh : synchronise les machines de l'user"""
        self.refresh_from_db()
        try:
            user_ldap = LdapUser.objects.get(uidNumber=self.uid_number)
        except LdapUser.DoesNotExist:
            user_ldap = LdapUser(uidNumber=self.uid_number)
        if base:
            user_ldap.name = self.pseudo
            user_ldap.sn = self.pseudo
            user_ldap.dialupAccess = str(self.has_access())
            user_ldap.home_directory = '/home/' + self.pseudo
            user_ldap.mail = self.email
            user_ldap.given_name = self.surname.lower() + '_' + self.name.lower()[:3]
            user_ldap.gid = LDAP['user_gid']
            user_ldap.user_password = self.password[:6] + self.password[7:]
            user_ldap.sambat_nt_password = self.pwd_ntlm.upper()
            if self.shell:
                user_ldap.login_shell = self.shell.shell
            if self.state == self.STATE_DISABLED:
                user_ldap.shadowexpire = str(0)
            else:
                user_ldap.shadowexpire = None
        if access_refresh:
            user_ldap.dialupAccess = str(self.has_access())
        if mac_refresh:
            user_ldap.macs = [inter.mac_bare() for inter in Interface.objects.filter(machine__in=Machine.objects.filter(user=self))]
        user_ldap.save()

    def ldap_del(self):
        """ Supprime la version ldap de l'user"""
        try:
            user_ldap = LdapUser.objects.get(name=self.pseudo)
            user_ldap.delete()
        except LdapUser.DoesNotExist:
            pass

    def notif_inscription(self):
        """ Prend en argument un objet user, envoie un mail de bienvenue """
        t = loader.get_template('users/email_welcome')
        assooptions, created = AssoOption.objects.get_or_create()
        mailmessageoptions, created = MailMessageOption.objects.get_or_create()
        general_options, created = GeneralOption.objects.get_or_create()
        c = Context({
            'nom': str(self.name) + ' ' + str(self.surname),
            'asso_name': assooptions.name,
            'asso_email': assooptions.contact,
            'welcome_mail_fr' : mailmessageoptions.welcome_mail_fr,
            'welcome_mail_en' : mailmessageoptions.welcome_mail_en,
            'pseudo':self.pseudo,
        })
        send_mail('Bienvenue au %(name)s / Welcome to %(name)s' % {'name': assooptions.name }, '',
        general_options.email_from, [self.email], html_message=t.render(c))
        return

    def reset_passwd_mail(self, request):
        """ Prend en argument un request, envoie un mail de réinitialisation de mot de pass """
        req = Request()
        req.type = Request.PASSWD
        req.user = self
        req.save()
        t = loader.get_template('users/email_passwd_request')
        options, created = AssoOption.objects.get_or_create()
        general_options, created = GeneralOption.objects.get_or_create()
        c = {
            'name': str(req.user.name) + ' ' + str(req.user.surname),
            'asso': options.name,
            'asso_mail': options.contact,
            'site_name': general_options.site_name,
            'url': request.build_absolute_uri(
            reverse('users:process', kwargs={'token': req.token})),
            'expire_in': str(general_options.req_expire_hrs) + ' heures',
            }
        send_mail('Changement de mot de passe du %(name)s / Password renewal for %(name)s' % {'name': options.name }, t.render(c),
        general_options.email_from, [req.user.email], fail_silently=False)
        return

    def autoregister_machine(self, mac_address, nas_type):
        """ Fonction appellée par freeradius. Enregistre la mac pour une machine inconnue 
        sur le compte de l'user"""
        all_interfaces = self.user_interfaces(active=False)
        options, created = OptionalMachine.objects.get_or_create() 
        if all_interfaces.count() > options.max_lambdauser_interfaces:
            return False, "Maximum de machines enregistrees atteinte"
        if not nas_type:
            return False, "Re2o ne sait pas à quel machinetype affecter cette machine"
        machine_type_cible = nas_type.machine_type
        try:
            machine_parent = Machine()
            machine_parent.user = self
            interface_cible = Interface()
            interface_cible.mac_address = mac_address
            interface_cible.type = machine_type_cible
            interface_cible.clean()
            machine_parent.clean()
            domain = Domain()
            domain.name = self.get_next_domain_name()
            domain.interface_parent = interface_cible
            domain.clean()
            machine_parent.save()
            interface_cible.machine = machine_parent
            interface_cible.save()
            domain.interface_parent = interface_cible
            domain.clean()
            domain.save()
        except Exception as e:
            return False, e
        return True, "Ok"

    def set_user_password(self, password):
        """ A utiliser de préférence, set le password en hash courrant et 
        dans la version ntlm"""
        self.set_password(password)
        self.pwd_ntlm = hashNT(password)
        return

    def get_next_domain_name(self):
        """Look for an available name for a new interface for
        this user by trying "pseudo0", "pseudo1", "pseudo2", ...
        """

        def simple_pseudo():
            return self.pseudo.replace('_', '-').lower()

        def composed_pseudo( n ):
            return simple_pseudo() + str(n)

        num = 0
        while Domain.objects.filter(name=composed_pseudo(num)) :
            num += 1
        return composed_pseudo(num)


    def __str__(self):
        return self.pseudo

@receiver(post_save, sender=User)
def user_post_save(sender, **kwargs):
    """ Synchronisation post_save : envoie le mail de bienvenue si creation
    Synchronise le ldap"""
    is_created = kwargs['created']
    user = kwargs['instance']
    if is_created:
        user.notif_inscription()
    user.ldap_sync(base=True, access_refresh=True, mac_refresh=False)
    regen('mailing')

@receiver(post_delete, sender=User)
def user_post_delete(sender, **kwargs):
    user = kwargs['instance']
    user.ldap_del()
    regen('mailing')

class ServiceUser(AbstractBaseUser):
    """ Classe des users daemons, règle leurs accès au ldap"""
    readonly = 'readonly'
    ACCESS = (
            ('auth', 'auth'),
            ('readonly', 'readonly'),
            ('usermgmt', 'usermgmt'),
            )

    PRETTY_NAME = "Utilisateurs de service"

    pseudo = models.CharField(max_length=32, unique=True, help_text="Doit contenir uniquement des lettres, chiffres, ou tirets", validators=[linux_user_validator])
    access_group = models.CharField(choices=ACCESS, default=readonly, max_length=32)
    comment = models.CharField(help_text="Commentaire", max_length=255, blank=True)

    USERNAME_FIELD = 'pseudo'
 
    objects = UserManager()

    def ldap_sync(self):
        """ Synchronisation du ServiceUser dans sa version ldap"""
        try:
            user_ldap = LdapServiceUser.objects.get(name=self.pseudo)
        except LdapServiceUser.DoesNotExist:
            user_ldap = LdapServiceUser(name=self.pseudo)
        user_ldap.user_password = self.password[:6] + self.password[7:]
        user_ldap.save()
        self.serviceuser_group_sync()

    def ldap_del(self):
        try:
            user_ldap = LdapServiceUser.objects.get(name=self.pseudo)
            user_ldap.delete()
        except LdapUser.DoesNotExist:
            pass
        self.serviceuser_group_sync()

    def serviceuser_group_sync(self):
        try:
            group = LdapServiceUserGroup.objects.get(name=self.access_group)
        except:
            group = LdapServiceUserGroup(name=self.access_group)
        group.members = list(LdapServiceUser.objects.filter(name__in=[user.pseudo for user in ServiceUser.objects.filter(access_group=self.access_group)]).values_list('dn', flat=True))
        group.save()

    def __str__(self):
        return self.pseudo

@receiver(post_save, sender=ServiceUser)
def service_user_post_save(sender, **kwargs):
    """ Synchronise un service user ldap après modification django"""
    service_user = kwargs['instance']
    service_user.ldap_sync()

@receiver(post_delete, sender=ServiceUser)
def service_user_post_delete(sender, **kwargs):
    """ Supprime un service user ldap après suppression django"""
    service_user = kwargs['instance']
    service_user.ldap_del()

class Right(models.Model):
    """ Couple droit/user. Peut-être aurait-on mieux fait ici d'utiliser un manytomany
    Ceci dit le résultat aurait été le même avec une table intermediaire"""
    PRETTY_NAME = "Droits affectés à des users"

    user = models.ForeignKey('User', on_delete=models.PROTECT)
    right = models.ForeignKey('ListRight', on_delete=models.PROTECT)

    class Meta:
        unique_together = ("user", "right")

    def __str__(self):
        return str(self.user)

@receiver(post_save, sender=Right)
def right_post_save(sender, **kwargs):
    """ Synchronise les users ldap groups avec les groupes de droits"""
    right = kwargs['instance'].right
    right.ldap_sync()

@receiver(post_delete, sender=Right)
def right_post_delete(sender, **kwargs):
    """ Supprime l'user du groupe"""
    right = kwargs['instance'].right
    right.ldap_sync()

class School(models.Model):
    """ Etablissement d'enseignement"""
    PRETTY_NAME = "Etablissements enregistrés"

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ListRight(models.Model):
    """ Ensemble des droits existants. Chaque droit crée un groupe ldap synchronisé, avec gid.
    Permet de gérer facilement les accès serveurs et autres
    La clef de recherche est le gid, pour cette raison là il n'est plus modifiable après creation"""
    PRETTY_NAME = "Liste des droits existants"

    listright = models.CharField(max_length=255, unique=True, validators=[RegexValidator('^[a-z]+$', message="Les groupes unix ne peuvent contenir que des lettres minuscules")])
    gid = models.IntegerField(unique=True, null=True)
    details = models.CharField(help_text="Description", max_length=255, blank=True)

    def __str__(self):
        return self.listright

    def ldap_sync(self):
        try:
            group_ldap = LdapUserGroup.objects.get(gid=self.gid)
        except LdapUserGroup.DoesNotExist:
            group_ldap = LdapUserGroup(gid=self.gid)
        group_ldap.name = self.listright
        group_ldap.members = [right.user.pseudo for right in Right.objects.filter(right=self)]
        group_ldap.save()

    def ldap_del(self):
        try:
            group_ldap = LdapUserGroup.objects.get(gid=self.gid)
            group_ldap.delete()
        except LdapUserGroup.DoesNotExist:
            pass

@receiver(post_save, sender=ListRight)
def listright_post_save(sender, **kwargs):
    """ Synchronise le droit ldap quand il est modifié"""
    right = kwargs['instance']
    right.ldap_sync()

@receiver(post_delete, sender=ListRight)
def listright_post_delete(sender, **kwargs):
    right = kwargs['instance']
    right.ldap_del()

class ListShell(models.Model):
    PRETTY_NAME = "Liste des shells disponibles"

    shell = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.shell

class Ban(models.Model):
    """ Bannissement. Actuellement a un effet tout ou rien.
    Gagnerait à être granulaire"""
    PRETTY_NAME = "Liste des bannissements"

    STATE_HARD = 0
    STATE_SOFT = 1
    STATE_BRIDAGE = 2
    STATES = (
            (0, 'HARD (aucun accès)'),
            (1, 'SOFT (accès local seulement)'),
            (2, 'BRIDAGE (bridage du débit)'),
            )

    user = models.ForeignKey('User', on_delete=models.PROTECT)
    raison = models.CharField(max_length=255)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField(help_text='%d/%m/%y %H:%M:%S')
    state = models.IntegerField(choices=STATES, default=STATE_HARD) 

    def notif_ban(self):
        """ Prend en argument un objet ban, envoie un mail de notification """
        general_options, created = GeneralOption.objects.get_or_create()
        t = loader.get_template('users/email_ban_notif')
        options, created = AssoOption.objects.get_or_create()
        c = Context({
            'name': str(self.user.name) + ' ' + str(self.user.surname),
            'raison': self.raison,
            'date_end': self.date_end,
            'asso_name' : options.name,
        })
        send_mail('Deconnexion disciplinaire', t.render(c),
        general_options.email_from, [self.user.email], fail_silently=False)
        return

    def is_active(self):
        return self.date_end > now

    def __str__(self):
        return str(self.user) + ' ' + str(self.raison)

@receiver(post_save, sender=Ban)
def ban_post_save(sender, **kwargs):
    """ Regeneration de tous les services après modification d'un ban"""
    ban = kwargs['instance']
    is_created = kwargs['created']
    user = ban.user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    regen('mailing')
    if is_created:
        ban.notif_ban()
        regen('dhcp')
        regen('mac_ip_list')
    if user.has_access():
        regen('dhcp')
        regen('mac_ip_list')

@receiver(post_delete, sender=Ban)
def ban_post_delete(sender, **kwargs):
    """ Regen de tous les services après suppression d'un ban"""
    user = kwargs['instance'].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    regen('mailing')
    regen('dhcp')
    regen('mac_ip_list')

class Whitelist(models.Model):
    PRETTY_NAME = "Liste des accès gracieux"

    user = models.ForeignKey('User', on_delete=models.PROTECT)
    raison = models.CharField(max_length=255)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField(help_text='%d/%m/%y %H:%M:%S')

    def is_active(self):
        return self.date_end > now

    def __str__(self):
        return str(self.user) + ' ' + str(self.raison)

@receiver(post_save, sender=Whitelist)
def whitelist_post_save(sender, **kwargs):
    whitelist = kwargs['instance']
    user = whitelist.user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    is_created = kwargs['created']
    regen('mailing')
    if is_created:
        regen('dhcp')
        regen('mac_ip_list')
    if user.has_access():
        regen('dhcp')
        regen('mac_ip_list')

@receiver(post_delete, sender=Whitelist)
def whitelist_post_delete(sender, **kwargs):
    user = kwargs['instance'].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    regen('mailing')
    regen('dhcp')
    regen('mac_ip_list')

class Request(models.Model):
    """ Objet request, générant une url unique de validation.
    Utilisé par exemple pour la generation du mot de passe et 
    sa réinitialisation"""
    PASSWD = 'PW'
    EMAIL = 'EM'
    TYPE_CHOICES = (
        (PASSWD, 'Mot de passe'),
        (EMAIL, 'Email'),
    )
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    token = models.CharField(max_length=32)
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    expires_at = models.DateTimeField()

    def save(self):
        if not self.expires_at:
            options, created = GeneralOption.objects.get_or_create()
            self.expires_at = timezone.now() \
                + datetime.timedelta(hours=options.req_expire_hrs)
        if not self.token:
            self.token = str(uuid.uuid4()).replace('-', '')  # remove hyphens
        super(Request, self).save()

class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = LDAP['base_user_dn']
    object_classes = ['inetOrgPerson','top','posixAccount','sambaSamAccount','radiusprofile', 'shadowAccount']

    # attributes
    gid = ldapdb.models.fields.IntegerField(db_column='gidNumber')
    name = ldapdb.models.fields.CharField(db_column='cn', max_length=200, primary_key=True)
    uid = ldapdb.models.fields.CharField(db_column='uid', max_length=200)
    uidNumber = ldapdb.models.fields.IntegerField(db_column='uidNumber', unique=True)
    sn = ldapdb.models.fields.CharField(db_column='sn', max_length=200)
    login_shell = ldapdb.models.fields.CharField(db_column='loginShell', max_length=200, blank=True, null=True)
    mail = ldapdb.models.fields.CharField(db_column='mail', max_length=200) 
    given_name = ldapdb.models.fields.CharField(db_column='givenName', max_length=200)
    home_directory = ldapdb.models.fields.CharField(db_column='homeDirectory', max_length=200)
    display_name = ldapdb.models.fields.CharField(db_column='displayName', max_length=200, blank=True, null=True)
    dialupAccess = ldapdb.models.fields.CharField(db_column='dialupAccess')
    sambaSID = ldapdb.models.fields.IntegerField(db_column='sambaSID', unique=True)
    user_password = ldapdb.models.fields.CharField(db_column='userPassword', max_length=200, blank=True, null=True)
    sambat_nt_password = ldapdb.models.fields.CharField(db_column='sambaNTPassword', max_length=200, blank=True, null=True)
    macs = ldapdb.models.fields.ListField(db_column='radiusCallingStationId', max_length=200, blank=True, null=True)
    shadowexpire = ldapdb.models.fields.CharField(db_column='shadowExpire', blank=True, null=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.sn = self.name
        self.uid = self.name
        self.sambaSID = self.uidNumber
        super(LdapUser, self).save(*args, **kwargs)

class LdapUserGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = LDAP['base_usergroup_dn']
    object_classes = ['posixGroup']

    # attributes
    gid = ldapdb.models.fields.IntegerField(db_column='gidNumber')
    members = ldapdb.models.fields.ListField(db_column='memberUid', blank=True)
    name = ldapdb.models.fields.CharField(db_column='cn', max_length=200, primary_key=True)

    def __str__(self):
        return self.name

class LdapServiceUser(ldapdb.models.Model):
    """
    Class for representing an LDAP userservice entry.
    """
    # LDAP meta-data
    base_dn = LDAP['base_userservice_dn']
    object_classes = ['applicationProcess','simpleSecurityObject']

    # attributes
    name = ldapdb.models.fields.CharField(db_column='cn', max_length=200, primary_key=True)
    user_password = ldapdb.models.fields.CharField(db_column='userPassword', max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

class LdapServiceUserGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP userservice entry.
    """
    # LDAP meta-data
    base_dn = LDAP['base_userservicegroup_dn']
    object_classes = ['groupOfNames']

    # attributes
    name = ldapdb.models.fields.CharField(db_column='cn', max_length=200, primary_key=True)
    members = ldapdb.models.fields.ListField(db_column='member', blank=True)

    def __str__(self):
        return self.name

