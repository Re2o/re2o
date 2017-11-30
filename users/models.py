# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz.
# Il  se veut agnostique au réseau considéré, de manière à être installable
# en quelques clics.
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
"""
Models de l'application users.

On défini ici des models django classiques:
- users, qui hérite de l'abstract base user de django. Permet de définit
un utilisateur du site (login, passwd, chambre, adresse, etc)
- les whiteslist
- les bannissements
- les établissements d'enseignement (school)
- les droits (right et listright)
- les utilisateurs de service (pour connexion automatique)

On défini aussi des models qui héritent de django-ldapdb :
- ldapuser
- ldapgroup
- ldapserviceuser

Ces utilisateurs ldap sont synchronisés à partir des objets
models sql classiques. Seuls certains champs essentiels sont
dupliqués.
"""


from __future__ import unicode_literals

import re
import uuid
import datetime

from django.db import models
from django.db.models import Q
from django import forms
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.template import Context, loader
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager
)
from django.core.validators import RegexValidator

from reversion import revisions as reversion

import ldapdb.models
import ldapdb.models.fields

from re2o.settings import RIGHTS_LINK, LDAP, GID_RANGES, UID_RANGES
from re2o.login import hashNT

from cotisations.models import Cotisation, Facture, Paiement, Vente
from machines.models import Domain, Interface, Machine, regen
from preferences.models import GeneralOption, AssoOption, OptionalUser
from preferences.models import OptionalMachine, MailMessageOption

DT_NOW = timezone.now()


# Utilitaires généraux


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
    uids = list(range(
        int(min(UID_RANGES['users'])),
        int(max(UID_RANGES['users']))
    ))
    try:
        used_uids = list(User.objects.values_list('uid_number', flat=True))
    except:
        used_uids = []
    free_uids = [id for id in uids if id not in used_uids]
    return min(free_uids)


def get_fresh_gid():
    """ Renvoie le plus petit gid libre  """
    gids = list(range(
        int(min(GID_RANGES['posix'])),
        int(max(GID_RANGES['posix']))
    ))
    used_gids = list(ListRight.objects.values_list('gid', flat=True))
    free_gids = [id for id in gids if id not in used_gids]
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


class UserManager(BaseUserManager):
    """User manager basique de django"""
    def _create_user(
            self,
            pseudo,
            surname,
            email,
            password=None,
            su=False
    ):
        if not pseudo:
            raise ValueError('Users must have an username')

        if not linux_user_check(pseudo):
            raise ValueError('Username shall only contain [a-z0-9-]')

        user = self.model(
            pseudo=pseudo,
            surname=surname,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        if su:
            user.make_admin()
        return user

    def create_user(self, pseudo, surname, email, password=None):
        """
        Creates and saves a User with the given pseudo, name, surname, email,
        and password.
        """
        return self._create_user(pseudo, surname, email, password, False)

    def create_superuser(self, pseudo, surname, email, password):
        """
        Creates and saves a superuser with the given pseudo, name, surname,
        email, and password.
        """
        return self._create_user(pseudo, surname, email, password, True)


class User(AbstractBaseUser):
    """ Definition de l'utilisateur de base.
    Champs principaux : name, surnname, pseudo, email, room, password
    Herite du django BaseUser et du système d'auth django"""
    PRETTY_NAME = "Utilisateurs (clubs et adhérents)"
    STATE_ACTIVE = 0
    STATE_DISABLED = 1
    STATE_ARCHIVE = 2
    STATES = (
        (0, 'STATE_ACTIVE'),
        (1, 'STATE_DISABLED'),
        (2, 'STATE_ARCHIVE'),
    )

    def auto_uid():
        """Renvoie un uid libre"""
        return get_fresh_user_uid()

    surname = models.CharField(max_length=255)
    pseudo = models.CharField(
        max_length=32,
        unique=True,
        help_text="Doit contenir uniquement des lettres, chiffres, ou tirets",
        validators=[linux_user_validator]
    )
    email = models.EmailField()
    school = models.ForeignKey(
        'School',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    shell = models.ForeignKey(
        'ListShell',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    comment = models.CharField(
        help_text="Commentaire, promo",
        max_length=255,
        blank=True
    )
    pwd_ntlm = models.CharField(max_length=255)
    state = models.IntegerField(choices=STATES, default=STATE_ACTIVE)
    registered = models.DateTimeField(auto_now_add=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    uid_number = models.PositiveIntegerField(default=auto_uid, unique=True)
    rezo_rez_uid = models.PositiveIntegerField(unique=True, blank=True, null=True)

    USERNAME_FIELD = 'pseudo'
    REQUIRED_FIELDS = ['surname', 'email']

    objects = UserManager()

    @cached_property
    def name(self):
        """Si il s'agit d'un adhérent, on renvoie le prénom"""
        if self.is_class_adherent:
            return self.adherent.name
        else:
            return ''

    @cached_property
    def room(self):
        """Alias vers room """
        if self.is_class_adherent:
            return self.adherent.room
        elif self.is_class_club:
            return self.club.room
        else:
            raise NotImplementedError("Type inconnu")

    @cached_property
    def class_name(self):
        """Renvoie si il s'agit d'un adhérent ou d'un club"""
        if hasattr(self, 'adherent'):
            return "Adherent"
        elif hasattr(self, 'club'):
            return "Club"
        else:
            raise NotImplementedError("Type inconnu")

    @cached_property
    def is_class_club(self):
        return hasattr(self, 'club')

    @cached_property
    def is_class_adherent(self):
        return hasattr(self, 'adherent')

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
        """ Change la valeur de admin à true ou false suivant la valeur de
        value"""
        if value and not self.is_admin:
            self.make_admin()
        elif not value and self.is_admin:
            self.un_admin()

    def get_full_name(self):
        """ Renvoie le nom complet de l'user formaté nom/prénom"""
        name = self.name
        if name:
            return '%s %s' % (name, self.surname)
        else:
            return self.surname

    def get_short_name(self):
        """ Renvoie seulement le nom"""
        return self.surname

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
        """Ne sert à rien"""
        return True

    def has_right(self, right):
        """ Renvoie si un user a un right donné. Crée le right si il n'existe
        pas"""
        try:
            list_right = ListRight.objects.get(listright=right)
        except:
            list_right = ListRight(listright=right, gid=get_fresh_gid())
            list_right.save()
        return Right.objects.filter(user=self).filter(
            right=list_right
        ).exists()

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
        return self.has_right('cableur') or self.has_right('bureau') or\
            self.has_right('infra') or self.has_right('bofh')

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
        date_max = Cotisation.objects.filter(
            vente__in=Vente.objects.filter(
                facture__in=Facture.objects.filter(
                    user=self
                ).exclude(valid=False)
            )
        ).filter(
            Q(type_cotisation='All') | Q(type_cotisation='Adhesion')
        ).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    def end_connexion(self):
        """ Renvoie la date de fin de connexion d'un user. Examine les objets
        cotisation"""
        date_max = Cotisation.objects.filter(
            vente__in=Vente.objects.filter(
                facture__in=Facture.objects.filter(
                    user=self
                ).exclude(valid=False)
            )
        ).filter(
            Q(type_cotisation='All') | Q(type_cotisation='Connexion')
        ).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    def is_adherent(self):
        """ Renvoie True si l'user est adhérent : si
        self.end_adhesion()>now"""
        end = self.end_adhesion()
        if not end:
            return False
        elif end < DT_NOW:
            return False
        else:
            return True

    def is_connected(self):
        """ Renvoie True si l'user est adhérent : si
        self.end_adhesion()>now et end_connexion>now"""
        end = self.end_connexion()
        if not end:
            return False
        elif end < DT_NOW:
            return False
        else:
            return self.is_adherent()

    @cached_property
    def end_ban(self):
        """ Renvoie la date de fin de ban d'un user, False sinon """
        date_max = Ban.objects.filter(
            user=self
        ).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    @cached_property
    def end_whitelist(self):
        """ Renvoie la date de fin de whitelist d'un user, False sinon """
        date_max = Whitelist.objects.filter(
            user=self
        ).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    @cached_property
    def is_ban(self):
        """ Renvoie si un user est banni ou non """
        end = self.end_ban
        if not end:
            return False
        elif end < DT_NOW:
            return False
        else:
            return True

    @cached_property
    def is_whitelisted(self):
        """ Renvoie si un user est whitelisté ou non """
        end = self.end_whitelist
        if not end:
            return False
        elif end < DT_NOW:
            return False
        else:
            return True

    def has_access(self):
        """ Renvoie si un utilisateur a accès à internet """
        return self.state == User.STATE_ACTIVE\
            and not self.is_ban and (self.is_connected() or self.is_whitelisted)

    def end_access(self):
        """ Renvoie la date de fin normale d'accès (adhésion ou whiteliste)"""
        if not self.end_connexion():
            if not self.end_whitelist:
                return None
            else:
                return self.end_whitelist
        else:
            if not self.end_whitelist:
                return self.end_connexion()
            else:
                return max(self.end_connexion(), self.end_whitelist)

    @cached_property
    def solde(self):
        """ Renvoie le solde d'un user. Vérifie que l'option solde est
        activé, retourne 0 sinon.
        Somme les crédits de solde et retire les débit payés par solde"""
        options, _created = OptionalUser.objects.get_or_create()
        user_solde = options.user_solde
        if user_solde:
            solde_object, _created = Paiement.objects.get_or_create(
                moyen='Solde'
            )
            somme_debit = Vente.objects.filter(
                facture__in=Facture.objects.filter(
                    user=self,
                    paiement=solde_object
                )
            ).aggregate(
                total=models.Sum(
                    models.F('prix')*models.F('number'),
                    output_field=models.FloatField()
                )
            )['total'] or 0
            somme_credit = Vente.objects.filter(
                facture__in=Facture.objects.filter(user=self),
                name="solde"
            ).aggregate(
                total=models.Sum(
                    models.F('prix')*models.F('number'),
                    output_field=models.FloatField()
                )
            )['total'] or 0
            return somme_credit - somme_debit
        else:
            return 0

    def user_interfaces(self, active=True):
        """ Renvoie toutes les interfaces dont les machines appartiennent à
        self. Par defaut ne prend que les interfaces actives"""
        return Interface.objects.filter(
            machine__in=Machine.objects.filter(user=self, active=active)
        ).select_related('domain__extension')

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
        """ Archive l'user : appelle unassign_ips() puis passe state à
        ARCHIVE"""
        self.unassign_ips()
        self.state = User.STATE_ARCHIVE

    def unarchive(self):
        """ Désarchive l'user : réassigne ses ip et le passe en state
        ACTIVE"""
        self.assign_ips()
        self.state = User.STATE_ACTIVE

    def has_module_perms(self, app_label):
        """True, a toutes les permissions de module"""
        return True

    def make_admin(self):
        """ Make User admin """
        user_admin_right = Right(user=self, right=get_admin_right())
        user_admin_right.save()

    def un_admin(self):
        """Supprime les droits admin d'un user"""
        try:
            user_right = Right.objects.get(user=self, right=get_admin_right())
        except Right.DoesNotExist:
            return
        user_right.delete()

    def ldap_sync(self, base=True, access_refresh=True, mac_refresh=True, group_refresh=False):
        """ Synchronisation du ldap. Synchronise dans le ldap les attributs de
        self
        Options : base : synchronise tous les attributs de base - nom, prenom,
        mail, password, shell, home
        access_refresh : synchronise le dialup_access notant si l'user a accès
        aux services
        mac_refresh : synchronise les machines de l'user
        group_refresh : synchronise les group de l'user
        Si l'instance n'existe pas, on crée le ldapuser correspondant"""
        self.refresh_from_db()
        try:
            user_ldap = LdapUser.objects.get(uidNumber=self.uid_number)
        except LdapUser.DoesNotExist:
            user_ldap = LdapUser(uidNumber=self.uid_number)
            base = True
            access_refresh = True
            mac_refresh = True
        if base:
            user_ldap.name = self.pseudo
            user_ldap.sn = self.pseudo
            user_ldap.dialupAccess = str(self.has_access())
            user_ldap.home_directory = '/home/' + self.pseudo
            user_ldap.mail = self.email
            user_ldap.given_name = self.surname.lower() + '_'\
                + self.name.lower()[:3]
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
            user_ldap.macs = [str(mac) for mac in Interface.objects.filter(
                machine__user=self
            ).values_list('mac_address', flat=True).distinct()]
        if group_refresh:
            for right in Right.objects.filter(user=self):
                right.right.ldap_sync()
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
        template = loader.get_template('users/email_welcome')
        assooptions, _created = AssoOption.objects.get_or_create()
        mailmessageoptions, _created = MailMessageOption\
            .objects.get_or_create()
        general_options, _created = GeneralOption.objects.get_or_create()
        context = Context({
            'nom': self.get_full_name(),
            'asso_name': assooptions.name,
            'asso_email': assooptions.contact,
            'welcome_mail_fr': mailmessageoptions.welcome_mail_fr,
            'welcome_mail_en': mailmessageoptions.welcome_mail_en,
            'pseudo': self.pseudo,
        })
        send_mail(
            'Bienvenue au %(name)s / Welcome to %(name)s' % {
                'name': assooptions.name
                },
            '',
            general_options.email_from,
            [self.email],
            html_message=template.render(context)
        )
        return

    def reset_passwd_mail(self, request):
        """ Prend en argument un request, envoie un mail de
        réinitialisation de mot de pass """
        req = Request()
        req.type = Request.PASSWD
        req.user = self
        req.save()
        template = loader.get_template('users/email_passwd_request')
        options, _created = AssoOption.objects.get_or_create()
        general_options, _created = GeneralOption.objects.get_or_create()
        context = {
            'name': req.user.get_full_name(),
            'asso': options.name,
            'asso_mail': options.contact,
            'site_name': general_options.site_name,
            'url': request.build_absolute_uri(
                reverse('users:process', kwargs={'token': req.token})),
            'expire_in': str(general_options.req_expire_hrs) + ' heures',
            }
        send_mail(
            'Changement de mot de passe du %(name)s / Password\
            renewal for %(name)s' % {'name': options.name},
            template.render(context),
            general_options.email_from,
            [req.user.email],
            fail_silently=False
        )
        return

    def autoregister_machine(self, mac_address, nas_type):
        """ Fonction appellée par freeradius. Enregistre la mac pour
        une machine inconnue sur le compte de l'user"""
        all_interfaces = self.user_interfaces(active=False)
        options, _created = OptionalMachine.objects.get_or_create()
        if all_interfaces.count() > options.max_lambdauser_interfaces:
            return False, "Maximum de machines enregistrees atteinte"
        if not nas_type:
            return False, "Re2o ne sait pas à quel machinetype affecter cette\
            machine"
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
            self.notif_auto_newmachine(interface_cible)
        except Exception as error:
            return False, error
        return True, "Ok"

    def notif_auto_newmachine(self, interface):
        """Notification mail lorsque une machine est automatiquement
        ajoutée par le radius"""
        template = loader.get_template('users/email_auto_newmachine')
        assooptions, _created = AssoOption.objects.get_or_create()
        general_options, _created = GeneralOption.objects.get_or_create()
        context = Context({
            'nom': self.get_full_name(),
            'mac_address' : interface.mac_address,
            'asso_name': assooptions.name,
            'interface_name' : interface.domain,
            'asso_email': assooptions.contact,
            'pseudo': self.pseudo,
        })
        send_mail(
            "Ajout automatique d'une machine / New machine autoregistered",
            '',
            general_options.email_from,
            [self.email],
            html_message=template.render(context)
        )
        return

    def set_user_password(self, password):
        """ A utiliser de préférence, set le password en hash courrant et
        dans la version ntlm"""
        self.set_password(password)
        self.pwd_ntlm = hashNT(password)
        return

    def get_next_domain_name(self):
        """Look for an available name for a new interface for
        this user by trying "pseudo0", "pseudo1", "pseudo2", ...

        Recherche un nom disponible, pour une machine. Doit-être
        unique, concatène le nom, le pseudo et le numero de machine
        """

        def simple_pseudo():
            """Renvoie le pseudo sans underscore (compat dns)"""
            return self.pseudo.replace('_', '-').lower()

        def composed_pseudo(name):
            """Renvoie le resultat de simplepseudo et rajoute le nom"""
            return simple_pseudo() + str(name)

        num = 0
        while Domain.objects.filter(name=composed_pseudo(num)):
            num += 1
        return composed_pseudo(num)

    def can_create(user):
        options, _created = OptionalUser.objects.get_or_create()
        if options.all_can_create:
            return True, None
        else:
            return user.has_perms(('cableur',)), u"Vous n'avez pas le\
                    droit de créer un utilisateur"

    def can_edit(self, user):
        if self.is_class_club and user.is_class_adherent:
            if self == user or user.has_perms(('cableur',)) or\
                user.adherent in self.club.administrators.all():
                return True, None
            else:
                return False, u"Vous n'avez pas le droit d'éditer ce club"
        else:
            if self == user or user.has_perms(('cableur',)):
                return True, None
            else:
                return False, u"Vous ne pouvez éditer un autre utilisateur que vous même"

    def can_view(self, user):
        if self.is_class_club and user.is_class_adherent:
            if self == user or user.has_perms(('cableur',)) or\
                user.adherent in self.club.administrators.all() or\
                user.adherent in self.club.members.all():
                return True, None
            else:
                return False, u"Vous n'avez pas le droit de voir ce club"
        else:
            if self == user or user.has_perms(('cableur',)):
                return True, None
            else:
                return False, u"Vous ne pouvez voir un autre utilisateur que vous même"

    def get_instance(userid):
        return User.objects.get(pk=userid)

    def __str__(self):
        return self.pseudo


class Adherent(User):
    PRETTY_NAME = "Adhérents"
    name = models.CharField(max_length=255)
    room = models.OneToOneField(
        'topologie.Room',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    pass



class Club(User):
    PRETTY_NAME = "Clubs"
    room = models.ForeignKey(
        'topologie.Room',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    administrators = models.ManyToManyField(
        blank=True,
        to='users.Adherent',
        related_name='club_administrator'
    )
    members = models.ManyToManyField(
        blank=True,
        to='users.Adherent',
        related_name='club_members'
    )

    pass


@receiver(post_save, sender=Adherent)
@receiver(post_save, sender=Club)
@receiver(post_save, sender=User)
def user_post_save(sender, **kwargs):
    """ Synchronisation post_save : envoie le mail de bienvenue si creation
    Synchronise le ldap"""
    is_created = kwargs['created']
    user = kwargs['instance']
    if is_created:
        user.notif_inscription()
    user.ldap_sync(base=True, access_refresh=True, mac_refresh=False, group_refresh=True)
    regen('mailing')


@receiver(post_delete, sender=Adherent)
@receiver(post_delete, sender=Club)
@receiver(post_delete, sender=User)
def user_post_delete(sender, **kwargs):
    """Post delete d'un user, on supprime son instance ldap"""
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

    pseudo = models.CharField(
        max_length=32,
        unique=True,
        help_text="Doit contenir uniquement des lettres, chiffres, ou tirets",
        validators=[linux_user_validator]
    )
    access_group = models.CharField(
        choices=ACCESS,
        default=readonly,
        max_length=32
    )
    comment = models.CharField(
        help_text="Commentaire",
        max_length=255,
        blank=True
    )

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
        """Suppression de l'instance ldap d'un service user"""
        try:
            user_ldap = LdapServiceUser.objects.get(name=self.pseudo)
            user_ldap.delete()
        except LdapUser.DoesNotExist:
            pass
        self.serviceuser_group_sync()

    def serviceuser_group_sync(self):
        """Synchronise le groupe et les droits de groupe dans le ldap"""
        try:
            group = LdapServiceUserGroup.objects.get(name=self.access_group)
        except:
            group = LdapServiceUserGroup(name=self.access_group)
        group.members = list(LdapServiceUser.objects.filter(
            name__in=[user.pseudo for user in ServiceUser.objects.filter(
                access_group=self.access_group
            )]).values_list('dn', flat=True))
        group.save()

    def __str__(self):
        return self.pseudo

    def can_create(user):
        options, _created = OptionalUser.objects.get_or_create()
        if options.all_can_create:
            return True, None
        else:
            return user.has_perms(('infra',)), u"Vous n'avez pas le droit de\
                créer un service user"

    def can_edit(instance, user):
        return user.has_perms(('infra',)), u"Vous n'avez pas le droit d'éditer\
            les services users"

    def get_instance(userid):
        return ServiceUser.objects.get(pk=userid)

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
    """ Couple droit/user. Peut-être aurait-on mieux fait ici d'utiliser un
    manytomany
    Ceci dit le résultat aurait été le même avec une table intermediaire"""
    PRETTY_NAME = "Droits affectés à des users"

    user = models.ForeignKey('User', on_delete=models.PROTECT)
    right = models.ForeignKey('ListRight', on_delete=models.PROTECT)

    class Meta:
        unique_together = ("user", "right")

    def __str__(self):
        return str(self.user)

    def can_create(user):
        return user.has_perms('bureau'), u"Vous n'avez pas le droit de\
            créer des droits"


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
    """ Ensemble des droits existants. Chaque droit crée un groupe
    ldap synchronisé, avec gid.
    Permet de gérer facilement les accès serveurs et autres
    La clef de recherche est le gid, pour cette raison là
    il n'est plus modifiable après creation"""
    PRETTY_NAME = "Liste des droits existants"

    listright = models.CharField(
        max_length=255,
        unique=True,
        validators=[RegexValidator(
            '^[a-z]+$',
            message="Les groupes unix ne peuvent contenir\
            que des lettres minuscules"
        )]
    )
    gid = models.PositiveIntegerField(unique=True, null=True)
    details = models.CharField(
        help_text="Description",
        max_length=255,
        blank=True
    )

    def __str__(self):
        return self.listright

    def ldap_sync(self):
        """Sychronise les groups ldap avec le model listright coté django"""
        try:
            group_ldap = LdapUserGroup.objects.get(gid=self.gid)
        except LdapUserGroup.DoesNotExist:
            group_ldap = LdapUserGroup(gid=self.gid)
        group_ldap.name = self.listright
        group_ldap.members = [right.user.pseudo for right
                              in Right.objects.filter(right=self)]
        group_ldap.save()

    def ldap_del(self):
        """Supprime un groupe ldap"""
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
    """Suppression d'un groupe ldap après suppression coté django"""
    right = kwargs['instance']
    right.ldap_del()


class ListShell(models.Model):
    """Un shell possible. Pas de check si ce shell existe, les
    admin sont des grands"""
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
        general_options, _created = GeneralOption.objects.get_or_create()
        template = loader.get_template('users/email_ban_notif')
        options, _created = AssoOption.objects.get_or_create()
        context = Context({
            'name': self.user.get_full_name(),
            'raison': self.raison,
            'date_end': self.date_end,
            'asso_name': options.name,
        })
        send_mail(
            'Deconnexion disciplinaire',
            template.render(context),
            general_options.email_from,
            [self.user.email],
            fail_silently=False
        )
        return

    def is_active(self):
        """Ce ban est-il actif?"""
        return self.date_end > DT_NOW

    def __str__(self):
        return str(self.user) + ' ' + str(self.raison)

    def can_create(user):
        return user.has_perms(('bofh',)), u"Vous n'avez pas le droit de\
            créer des bannissement"


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
    """Accès à titre gracieux. L'utilisateur ne paye pas; se voit
    accorder un accès internet pour une durée défini. Moins
    fort qu'un ban quel qu'il soit"""
    PRETTY_NAME = "Liste des accès gracieux"

    user = models.ForeignKey('User', on_delete=models.PROTECT)
    raison = models.CharField(max_length=255)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField(help_text='%d/%m/%y %H:%M:%S')

    def is_active(self):
        return self.date_end > DT_NOW

    def __str__(self):
        return str(self.user) + ' ' + str(self.raison)


@receiver(post_save, sender=Whitelist)
def whitelist_post_save(sender, **kwargs):
    """Après modification d'une whitelist, on synchronise les services
    et on lui permet d'avoir internet"""
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
    """Après suppression d'une whitelist, on supprime l'accès internet
    en forçant la régénration"""
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
            options, _created = GeneralOption.objects.get_or_create()
            self.expires_at = DT_NOW \
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
    object_classes = ['inetOrgPerson', 'top', 'posixAccount',
                      'sambaSamAccount', 'radiusprofile',
                      'shadowAccount']

    # attributes
    gid = ldapdb.models.fields.IntegerField(db_column='gidNumber')
    name = ldapdb.models.fields.CharField(
        db_column='cn',
        max_length=200,
        primary_key=True
    )
    uid = ldapdb.models.fields.CharField(db_column='uid', max_length=200)
    uidNumber = ldapdb.models.fields.IntegerField(
        db_column='uidNumber',
        unique=True
    )
    sn = ldapdb.models.fields.CharField(db_column='sn', max_length=200)
    login_shell = ldapdb.models.fields.CharField(
        db_column='loginShell',
        max_length=200,
        blank=True,
        null=True
    )
    mail = ldapdb.models.fields.CharField(db_column='mail', max_length=200)
    given_name = ldapdb.models.fields.CharField(
        db_column='givenName',
        max_length=200
    )
    home_directory = ldapdb.models.fields.CharField(
        db_column='homeDirectory',
        max_length=200
    )
    display_name = ldapdb.models.fields.CharField(
        db_column='displayName',
        max_length=200,
        blank=True,
        null=True
    )
    dialupAccess = ldapdb.models.fields.CharField(db_column='dialupAccess')
    sambaSID = ldapdb.models.fields.IntegerField(
        db_column='sambaSID',
        unique=True
    )
    user_password = ldapdb.models.fields.CharField(
        db_column='userPassword',
        max_length=200,
        blank=True,
        null=True
    )
    sambat_nt_password = ldapdb.models.fields.CharField(
        db_column='sambaNTPassword',
        max_length=200,
        blank=True,
        null=True
    )
    macs = ldapdb.models.fields.ListField(
        db_column='radiusCallingStationId',
        max_length=200,
        blank=True,
        null=True
    )
    shadowexpire = ldapdb.models.fields.CharField(
        db_column='shadowExpire',
        blank=True,
        null=True
    )

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
    Class for representing an LDAP group entry.

    Un groupe ldap
    """
    # LDAP meta-data
    base_dn = LDAP['base_usergroup_dn']
    object_classes = ['posixGroup']

    # attributes
    gid = ldapdb.models.fields.IntegerField(db_column='gidNumber')
    members = ldapdb.models.fields.ListField(db_column='memberUid', blank=True)
    name = ldapdb.models.fields.CharField(
        db_column='cn',
        max_length=200,
        primary_key=True
    )

    def __str__(self):
        return self.name


class LdapServiceUser(ldapdb.models.Model):
    """
    Class for representing an LDAP userservice entry.

    Un user de service coté ldap
    """
    # LDAP meta-data
    base_dn = LDAP['base_userservice_dn']
    object_classes = ['applicationProcess', 'simpleSecurityObject']

    # attributes
    name = ldapdb.models.fields.CharField(
        db_column='cn',
        max_length=200,
        primary_key=True
    )
    user_password = ldapdb.models.fields.CharField(
        db_column='userPassword',
        max_length=200,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class LdapServiceUserGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP userservice entry.

    Un group user de service coté ldap. Dans userservicegroupdn
    (voir dans settings_local.py)
    """
    # LDAP meta-data
    base_dn = LDAP['base_userservicegroup_dn']
    object_classes = ['groupOfNames']

    # attributes
    name = ldapdb.models.fields.CharField(
        db_column='cn',
        max_length=200,
        primary_key=True
    )
    members = ldapdb.models.fields.ListField(
        db_column='member',
        blank=True
    )

    def __str__(self):
        return self.name
