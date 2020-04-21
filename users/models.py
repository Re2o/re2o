# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz.
# Il  se veut agnostique au réseau considéré, de manière à être installable
# en quelques clics.
#
# Copyright © 2017-2020  Gabriel Détraz
# Copyright © 2017-2020  Lara Kermarec
# Copyright © 2017-2020  Augustin Lemesle
# Copyright © 2017-2020  Hugo Levy--Falk
# Copyright © 2017-2020  Jean-Romain Garnier
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
import sys

from django.db import models
from django.db.models import Q
from django import forms
from django.forms import ValidationError
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.template import loader
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
)
from django.core.validators import RegexValidator
import traceback
from django.utils.translation import ugettext_lazy as _

from reversion import revisions as reversion

import ldapdb.models
import ldapdb.models.fields

from re2o.settings import LDAP, GID_RANGES, UID_RANGES
from re2o.field_permissions import FieldPermissionModelMixin
from re2o.mixins import AclMixin, RevMixin
from re2o.base import smtp_check
from re2o.mail_utils import send_mail

from cotisations.models import Cotisation, Facture, Paiement, Vente
from machines.models import Domain, Interface, Machine, regen
from preferences.models import GeneralOption, AssoOption, OptionalUser
from preferences.models import OptionalMachine, MailMessageOption


# Utilitaires généraux


def linux_user_check(login):
    """ Validation du pseudo pour respecter les contraintes unix"""
    UNIX_LOGIN_PATTERN = re.compile("^[a-z][a-z0-9-]*[$]?$")
    return UNIX_LOGIN_PATTERN.match(login)


def linux_user_validator(login):
    """ Retourne une erreur de validation si le login ne respecte
    pas les contraintes unix (maj, min, chiffres ou tiret)"""
    if not linux_user_check(login):
        raise forms.ValidationError(
            _("The username \"%(label)s\" contains forbidden characters."),
            params={"label": login},
        )


def get_fresh_user_uid():
    """ Renvoie le plus petit uid non pris. Fonction très paresseuse """
    uids = list(range(int(min(UID_RANGES["users"])), int(max(UID_RANGES["users"]))))
    try:
        used_uids = list(User.objects.values_list("uid_number", flat=True))
    except:
        used_uids = []
    free_uids = [id for id in uids if id not in used_uids]
    return min(free_uids)


def get_fresh_gid():
    """ Renvoie le plus petit gid libre  """
    gids = list(range(int(min(GID_RANGES["posix"])), int(max(GID_RANGES["posix"]))))
    used_gids = list(ListRight.objects.values_list("gid", flat=True))
    free_gids = [id for id in gids if id not in used_gids]
    return min(free_gids)


class UserManager(BaseUserManager):
    """User manager basique de django"""

    def _create_user(self, pseudo, surname, email, password=None, su=False):
        if not pseudo:
            raise ValueError(_("Users must have an username."))

        if not linux_user_check(pseudo):
            raise ValueError(_("Username should only contain [a-z0-9-]."))

        user = Adherent(
            pseudo=pseudo,
            surname=surname,
            name=surname,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.confirm_mail()
        if su:
            user.is_superuser = True
        user.save(using=self._db)
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


class User(
    RevMixin, FieldPermissionModelMixin, AbstractBaseUser, PermissionsMixin, AclMixin
):
    """ Definition de l'utilisateur de base.
    Champs principaux : name, surnname, pseudo, email, room, password
    Herite du django BaseUser et du système d'auth django"""

    STATE_ACTIVE = 0
    STATE_DISABLED = 1
    STATE_ARCHIVE = 2
    STATE_NOT_YET_ACTIVE = 3
    STATE_FULL_ARCHIVE = 4
    STATES = (
        (0, _("Active")),
        (1, _("Disabled")),
        (2, _("Archived")),
        (3, _("Not yet active")),
        (4, _("Fully archived")),
    )

    EMAIL_STATE_VERIFIED = 0
    EMAIL_STATE_UNVERIFIED = 1
    EMAIL_STATE_PENDING = 2
    EMAIL_STATES = (
        (0, _("Confirmed")),
        (1, _("Not confirmed")),
        (2, _("Waiting for email confirmation")),
    )

    surname = models.CharField(max_length=255)
    pseudo = models.CharField(
        max_length=32,
        unique=True,
        help_text=_("Must only contain letters, numerals or dashes."),
        validators=[linux_user_validator],
    )
    email = models.EmailField(
        blank=True,
        default="",
        help_text=_("External email address allowing us to contact you."),
    )
    local_email_redirect = models.BooleanField(
        default=False,
        help_text=_(
            "Enable redirection of the local email messages to the"
            " main email address."
        ),
    )
    local_email_enabled = models.BooleanField(
        default=False, help_text=_("Enable the local email account.")
    )
    school = models.ForeignKey(
        "School", on_delete=models.PROTECT, null=True, blank=True
    )
    shell = models.ForeignKey(
        "ListShell", on_delete=models.PROTECT, null=True, blank=True
    )
    comment = models.CharField(
        help_text=_("Comment, school year."), max_length=255, blank=True
    )
    pwd_ntlm = models.CharField(max_length=255)
    state = models.IntegerField(choices=STATES, default=STATE_NOT_YET_ACTIVE)
    email_state = models.IntegerField(choices=EMAIL_STATES, default=EMAIL_STATE_PENDING)
    registered = models.DateTimeField(auto_now_add=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    uid_number = models.PositiveIntegerField(default=get_fresh_user_uid, unique=True)
    rezo_rez_uid = models.PositiveIntegerField(unique=True, blank=True, null=True)
    shortcuts_enabled = models.BooleanField(
        verbose_name=_("enable shortcuts on Re2o website"), default=True
    )
    email_change_date = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "pseudo"
    REQUIRED_FIELDS = ["surname", "email"]

    objects = UserManager()
    request = None

    class Meta:
        permissions = (
            ("change_user_password", _("Can change the password of a user")),
            ("change_user_state", _("Can edit the state of a user")),
            ("change_user_force", _("Can force the move")),
            ("change_user_shell", _("Can edit the shell of a user")),
            (
                "change_user_groups",
                _("Can edit the groups of rights of a user (critical permission)"),
            ),
            ("change_all_users", _("Can edit all users, including those with rights")),
            ("view_user", _("Can view a user object")),
        )
        verbose_name = _("user (member or club)")
        verbose_name_plural = _("users (members or clubs)")

    @cached_property
    def name(self):
        """Si il s'agit d'un adhérent, on renvoie le prénom"""
        if self.is_class_adherent:
            return self.adherent.name
        else:
            return ""

    @cached_property
    def room(self):
        """Alias vers room """
        if self.is_class_adherent:
            return self.adherent.room
        elif self.is_class_club:
            return self.club.room
        else:
            raise NotImplementedError(_("Unknown type."))

    @cached_property
    def get_mail_addresses(self):
        if self.local_email_enabled:
            return self.emailaddress_set.all()
        return None

    @cached_property
    def get_mail(self):
        """Return the mail address choosen by the user"""
        if (
            not OptionalUser.get_cached_value("local_email_accounts_enabled")
            or not self.local_email_enabled
            or self.local_email_redirect
        ):
            return str(self.email)
        else:
            return str(self.emailaddress_set.get(local_part=self.pseudo.lower()))

    @cached_property
    def class_type(self):
        """Returns the type of that user; returns database keyname"""
        if hasattr(self, "adherent"):
            return "Adherent"
        elif hasattr(self, "club"):
            return "Club"
        else:
            raise NotImplementedError(_("Unknown type."))

    @cached_property
    def class_display(self):
        """Returns the typename of that user to display for user interface"""
        if hasattr(self, "adherent"):
            return _("Member")
        elif hasattr(self, "club"):
            return _("Club")
        else:
            raise NotImplementedError(_("Unknown type."))

    @cached_property
    def gid_number(self):
        """renvoie le gid par défaut des users"""
        return int(LDAP["user_gid"])

    @cached_property
    def is_class_club(self):
        """ Returns True if the object is a Club (subclassing User) """
        # TODO : change to isinstance (cleaner)
        return hasattr(self, "club")

    @cached_property
    def is_class_adherent(self):
        """ Returns True if the object is a Adherent (subclassing User) """
        # TODO : change to isinstance (cleaner)
        return hasattr(self, "adherent")

    @property
    def is_active(self):
        """ Renvoie si l'user est à l'état actif"""
        allow_archived = OptionalUser.get_cached_value("allow_archived_connexion")
        return (
            self.state == self.STATE_ACTIVE
            or self.state == self.STATE_NOT_YET_ACTIVE
            or (
                allow_archived
                and self.state in (self.STATE_ARCHIVE, self.STATE_FULL_ARCHIVE)
            )
        )

    def set_active(self):
        """Enable this user if he subscribed successfully one time before
        Reenable it if it was archived
        Do nothing if disabled or waiting for email confirmation"""
        if self.state == self.STATE_NOT_YET_ACTIVE:
            if self.facture_set.filter(valid=True).filter(
                Q(vente__type_cotisation="All") | Q(vente__type_cotisation="Adhesion")
            ).exists() or OptionalUser.get_cached_value("all_users_active"):
                self.state = self.STATE_ACTIVE
                self.save()
        if self.state == self.STATE_ARCHIVE or self.state == self.STATE_FULL_ARCHIVE:
            self.state = self.STATE_ACTIVE
            self.unarchive()
            self.save()

    @property
    def is_staff(self):
        """ Fonction de base django, renvoie si l'user est admin"""
        return self.is_admin

    @property
    def is_admin(self):
        """ Renvoie si l'user est admin"""
        admin, _ = Group.objects.get_or_create(name="admin")
        return self.is_superuser or admin in self.groups.all()

    def get_full_name(self):
        """ Renvoie le nom complet de l'user formaté nom/prénom"""
        name = self.name
        if name:
            return "%s %s" % (name, self.surname)
        else:
            return self.surname

    def get_short_name(self):
        """ Renvoie seulement le nom"""
        return self.surname

    @cached_property
    def gid(self):
        """return the default gid of user"""
        return LDAP["user_gid"]

    @property
    def get_shell(self):
        """ A utiliser de préférence, prend le shell par défaut
        si il n'est pas défini"""
        return self.shell or OptionalUser.get_cached_value("shell_default")

    @cached_property
    def home_directory(self):
        return "/home/" + self.pseudo

    @cached_property
    def get_shadow_expire(self):
        """Return the shadow_expire value for the user"""
        if self.state == self.STATE_DISABLED or self.email_state == self.EMAIL_STATE_UNVERIFIED:
            return str(0)
        else:
            return None

    def end_adhesion(self):
        """ Renvoie la date de fin d'adhésion d'un user. Examine les objets
        cotisation"""
        date_max = (
            Cotisation.objects.filter(
                vente__in=Vente.objects.filter(
                    facture__in=Facture.objects.filter(user=self).exclude(valid=False)
                )
            )
            .filter(Q(type_cotisation="All") | Q(type_cotisation="Adhesion"))
            .aggregate(models.Max("date_end"))["date_end__max"]
        )
        return date_max

    def end_connexion(self):
        """ Renvoie la date de fin de connexion d'un user. Examine les objets
        cotisation"""
        date_max = (
            Cotisation.objects.filter(
                vente__in=Vente.objects.filter(
                    facture__in=Facture.objects.filter(user=self).exclude(valid=False)
                )
            )
            .filter(Q(type_cotisation="All") | Q(type_cotisation="Connexion"))
            .aggregate(models.Max("date_end"))["date_end__max"]
        )
        return date_max

    def is_adherent(self):
        """ Renvoie True si l'user est adhérent : si
        self.end_adhesion()>now"""
        end = self.end_adhesion()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    def is_connected(self):
        """ Renvoie True si l'user est adhérent : si
        self.end_adhesion()>now et end_connexion>now"""
        end = self.end_connexion()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return self.is_adherent()

    def end_ban(self):
        """ Renvoie la date de fin de ban d'un user, False sinon """
        date_max = Ban.objects.filter(user=self).aggregate(models.Max("date_end"))[
            "date_end__max"
        ]
        return date_max

    def end_whitelist(self):
        """ Renvoie la date de fin de whitelist d'un user, False sinon """
        date_max = Whitelist.objects.filter(user=self).aggregate(
            models.Max("date_end")
        )["date_end__max"]
        return date_max

    def is_ban(self):
        """ Renvoie si un user est banni ou non """
        end = self.end_ban()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    def is_whitelisted(self):
        """ Renvoie si un user est whitelisté ou non """
        end = self.end_whitelist()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    def has_access(self):
        """ Renvoie si un utilisateur a accès à internet """
        return (
            self.state == User.STATE_ACTIVE
            and self.email_state != User.EMAIL_STATE_UNVERIFIED
            and not self.is_ban()
            and (self.is_connected() or self.is_whitelisted())
        ) or self == AssoOption.get_cached_value("utilisateur_asso")

    def end_access(self):
        """ Renvoie la date de fin normale d'accès (adhésion ou whiteliste)"""
        if not self.end_connexion():
            if not self.end_whitelist():
                return None
            else:
                return self.end_whitelist()
        else:
            if not self.end_whitelist():
                return self.end_connexion()
            else:
                return max(self.end_connexion(), self.end_whitelist())

    @cached_property
    def solde(self):
        """ Renvoie le solde d'un user.
        Somme les crédits de solde et retire les débit payés par solde"""
        solde_objects = Paiement.objects.filter(is_balance=True)
        somme_debit = (
            Vente.objects.filter(
                facture__in=Facture.objects.filter(
                    user=self, paiement__in=solde_objects, valid=True
                )
            ).aggregate(
                total=models.Sum(
                    models.F("prix") * models.F("number"),
                    output_field=models.DecimalField(),
                )
            )[
                "total"
            ]
            or 0
        )
        somme_credit = (
            Vente.objects.filter(
                facture__in=Facture.objects.filter(user=self, valid=True), name="solde"
            ).aggregate(
                total=models.Sum(
                    models.F("prix") * models.F("number"),
                    output_field=models.DecimalField(),
                )
            )[
                "total"
            ]
            or 0
        )
        return somme_credit - somme_debit

    @classmethod
    def users_interfaces(cls, users, active=True, all_interfaces=False):
        """ Renvoie toutes les interfaces dont les machines appartiennent à
        self. Par defaut ne prend que les interfaces actives"""
        if all_interfaces:
            return Interface.objects.filter(
                machine__in=Machine.objects.filter(user__in=users)
            ).select_related("domain__extension")
        else:
            return Interface.objects.filter(
                machine__in=Machine.objects.filter(user__in=users, active=active)
            ).select_related("domain__extension")

    def user_interfaces(self, active=True, all_interfaces=False):
        """ Renvoie toutes les interfaces dont les machines appartiennent à
        self. Par defaut ne prend que les interfaces actives"""
        return self.users_interfaces(
            [self], active=active, all_interfaces=all_interfaces
        )

    def assign_ips(self):
        """ Assign une ipv4 aux machines d'un user """
        interfaces = self.user_interfaces()
        with transaction.atomic(), reversion.create_revision():
            Interface.mass_assign_ipv4(interfaces)
            reversion.set_comment("IPv4 assignment")

    def unassign_ips(self):
        """ Désassigne les ipv4 aux machines de l'user"""
        interfaces = self.user_interfaces()
        with transaction.atomic(), reversion.create_revision():
            Interface.mass_unassign_ipv4(interfaces)
            reversion.set_comment("IPv4 unassignment")

    @classmethod
    def mass_unassign_ips(cls, users_list):
        interfaces = cls.users_interfaces(users_list)
        with transaction.atomic(), reversion.create_revision():
            Interface.mass_unassign_ipv4(interfaces)
            reversion.set_comment("IPv4 assignment")

    @classmethod
    def mass_disable_email(cls, queryset_users):
        """Disable email account and redirection"""
        queryset_users.update(local_email_enabled=False)
        queryset_users.update(local_email_redirect=False)

    @classmethod
    def mass_delete_data(cls, queryset_users):
        """This users will be completely archived, so only keep mandatory data"""
        cls.mass_disable_email(queryset_users)
        Machine.mass_delete(Machine.objects.filter(user__in=queryset_users))
        cls.ldap_delete_users(queryset_users)

    def disable_email(self):
        """Disable email account and redirection"""
        self.local_email_enabled = False
        self.local_email_redirect = False

    def delete_data(self):
        """This user will be completely archived, so only keep mandatory data"""
        self.disable_email()
        self.machine_set.all().delete()

    @classmethod
    def mass_archive(cls, users_list):
        """Mass Archive several users, take a queryset
        Copy Queryset to avoid eval problem with queryset update"""
        # Force eval of queryset
        bool(users_list)
        users_list = users_list.all()
        cls.mass_unassign_ips(users_list)
        users_list.update(state=User.STATE_ARCHIVE)

    @classmethod
    def mass_full_archive(cls, users_list):
        """Mass Archive several users, take a queryset
        Copy Queryset to avoid eval problem with queryset update"""
        # Force eval of queryset
        bool(users_list)
        users_list = users_list.all()
        cls.mass_unassign_ips(users_list)
        cls.mass_delete_data(users_list)
        users_list.update(state=User.STATE_FULL_ARCHIVE)

    def archive(self):
        """ Filling the user; no more active"""
        self.unassign_ips()

    def full_archive(self):
        """Full Archive = Archive + Service access complete deletion"""
        self.archive()
        self.delete_data()
        self.ldap_del()

    def unarchive(self):
        """Unfilling the user"""
        self.assign_ips()
        self.ldap_sync()

    def state_sync(self):
        """Archive, or unarchive, if the user was not active/or archived before"""
        if (
            self.__original_state != self.STATE_ACTIVE
            and self.state == self.STATE_ACTIVE
        ):
            self.unarchive()
        elif (
            self.__original_state != self.STATE_ARCHIVE
            and self.state == self.STATE_ARCHIVE
        ):
            self.archive()
        elif (
            self.__original_state != self.STATE_FULL_ARCHIVE
            and self.state == self.STATE_FULL_ARCHIVE
        ):
            self.full_archive()

    def ldap_sync(
        self, base=True, access_refresh=True, mac_refresh=True, group_refresh=False
    ):
        """ Synchronisation du ldap. Synchronise dans le ldap les attributs de
        self
        Options : base : synchronise tous les attributs de base - nom, prenom,
        mail, password, shell, home
        access_refresh : synchronise le dialup_access notant si l'user a accès
        aux services
        mac_refresh : synchronise les machines de l'user
        group_refresh : synchronise les group de l'user
        Si l'instance n'existe pas, on crée le ldapuser correspondant"""
        if sys.version_info[0] >= 3 and (
            self.state == self.STATE_ACTIVE
            or self.state == self.STATE_ARCHIVE
            or self.state == self.STATE_DISABLED
        ):
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
                user_ldap.home_directory = self.home_directory
                user_ldap.mail = self.get_mail
                user_ldap.given_name = (
                    self.surname.lower() + "_" + self.name.lower()[:3]
                )
                user_ldap.gid = LDAP["user_gid"]
                if "{SSHA}" in self.password or "{SMD5}" in self.password:
                    # We remove the extra $ added at import from ldap
                    user_ldap.user_password = self.password[:6] + self.password[7:]
                elif "{crypt}" in self.password:
                    # depending on the length, we need to remove or not a $
                    if len(self.password) == 41:
                        user_ldap.user_password = self.password
                    else:
                        user_ldap.user_password = self.password[:7] + self.password[8:]

                user_ldap.sambat_nt_password = self.pwd_ntlm.upper()
                if self.get_shell:
                    user_ldap.login_shell = str(self.get_shell)
                user_ldap.shadowexpire = self.get_shadow_expire
            if access_refresh:
                user_ldap.dialupAccess = str(self.has_access())
            if mac_refresh:
                user_ldap.macs = [
                    str(mac)
                    for mac in Interface.objects.filter(machine__user=self)
                    .values_list("mac_address", flat=True)
                    .distinct()
                ]
            if group_refresh:
                # Need to refresh all groups because we don't know which groups
                # were updated during edition of groups and the user may no longer
                # be part of the updated group (case of group removal)
                for group in Group.objects.all():
                    if hasattr(group, "listright"):
                        group.listright.ldap_sync()
            user_ldap.save()

    def ldap_del(self):
        """ Supprime la version ldap de l'user"""
        try:
            user_ldap = LdapUser.objects.get(name=self.pseudo)
            user_ldap.delete()
        except LdapUser.DoesNotExist:
            pass

    @classmethod
    def ldap_delete_users(cls, queryset_users):
        """Delete multiple users in ldap"""
        LdapUser.objects.filter(
            name__in=list(queryset_users.values_list("pseudo", flat=True))
        )

    def notif_inscription(self, request=None):
        """ Prend en argument un objet user, envoie un mail de bienvenue """
        template = loader.get_template("users/email_welcome")
        mailmessageoptions, _created = MailMessageOption.objects.get_or_create()
        context = {
            "nom": self.get_full_name(),
            "asso_name": AssoOption.get_cached_value("name"),
            "asso_email": AssoOption.get_cached_value("contact"),
            "welcome_mail_fr": mailmessageoptions.welcome_mail_fr,
            "welcome_mail_en": mailmessageoptions.welcome_mail_en,
            "pseudo": self.pseudo,
        }

        send_mail(
            request,
            "Bienvenue au %(name)s / Welcome to %(name)s"
            % {"name": AssoOption.get_cached_value("name")},
            "",
            GeneralOption.get_cached_value("email_from"),
            [self.email],
            html_message=template.render(context),
        )

    def reset_passwd_mail(self, request):
        """ Prend en argument un request, envoie un mail de
        réinitialisation de mot de pass """
        req = Request()
        req.type = Request.PASSWD
        req.user = self
        req.save()
        template = loader.get_template("users/email_passwd_request")
        context = {
            "name": req.user.get_full_name(),
            "asso": AssoOption.get_cached_value("name"),
            "asso_mail": AssoOption.get_cached_value("contact"),
            "site_name": GeneralOption.get_cached_value("site_name"),
            "url": request.build_absolute_uri(
                reverse("users:process", kwargs={"token": req.token})
            ),
            "expire_in": str(GeneralOption.get_cached_value("req_expire_hrs")),
        }

        send_mail(
            request,
            "Changement de mot de passe de %(name)s / Password change for "
            "%(name)s" % {"name": AssoOption.get_cached_value("name")},
            template.render(context),
            GeneralOption.get_cached_value("email_from"),
            [req.user.email],
            fail_silently=False,
        )

    def send_confirm_email_if_necessary(self, request):
        """Update the user's email state:
        * If the user changed email, it needs to be confirmed
        * If they're not fully archived, send a confirmation email

        Returns whether an email was sent"""
        # Only update the state if the email changed
        if self.__original_email == self.email:
            return False

        # If the user was previously in the PENDING or UNVERIFIED state,
        # we can't update email_change_date otherwise it would push back
        # their due date
        # However, if the user is in the VERIFIED state, we reset the date
        if self.email_state == self.EMAIL_STATE_VERIFIED:
            self.email_change_date = timezone.now()

        # Remember that the user needs to confirm their email address again
        self.email_state = self.EMAIL_STATE_PENDING
        self.save()

        # Fully archived users shouldn't get an email, so stop here
        if self.state == self.STATE_FULL_ARCHIVE:
            return False

        # Send the email
        self.confirm_email_address_mail(request)
        return True

    def trigger_email_changed_state(self, request):
        """Trigger an email, and changed values after email_state been manually updated"""
        if self.email_state == self.EMAIL_STATE_VERIFIED:
            return False

        self.email_change_date = timezone.now()
        self.save()

        self.confirm_email_address_mail(request)
        return True

    def confirm_email_before_date(self):
        if self.email_state == self.EMAIL_STATE_VERIFIED:
            return None

        days = OptionalUser.get_cached_value("disable_emailnotyetconfirmed")
        return self.email_change_date + timedelta(days=days)

    def confirm_email_address_mail(self, request):
        """Prend en argument un request, envoie un mail pour
        confirmer l'adresse"""
        # Delete all older requests for this user, that aren't for this email
        filter = Q(user=self) & Q(type=Request.EMAIL) & ~Q(email=self.email)
        Request.objects.filter(filter).delete()

        # Create the request and send the email
        req = Request()
        req.type = Request.EMAIL
        req.user = self
        req.email = self.email
        req.save()

        template = loader.get_template("users/email_confirmation_request")
        context = {
            "name": req.user.get_full_name(),
            "asso": AssoOption.get_cached_value("name"),
            "asso_mail": AssoOption.get_cached_value("contact"),
            "site_name": GeneralOption.get_cached_value("site_name"),
            "url": request.build_absolute_uri(
                reverse("users:process", kwargs={"token": req.token})
            ),
            "expire_in": str(GeneralOption.get_cached_value("req_expire_hrs")),
            "confirm_before_fr": self.confirm_email_before_date().strftime("%d/%m/%Y"),
            "confirm_before_en": self.confirm_email_before_date().strftime("%Y-%m-%d"),
        }

        send_mail(
            request,
            "Confirmation du mail de %(name)s / Email confirmation for "
            "%(name)s" % {"name": AssoOption.get_cached_value("name")},
            template.render(context),
            GeneralOption.get_cached_value("email_from"),
            [req.user.email],
            fail_silently=False,
        )
        return

    def autoregister_machine(self, mac_address, nas_type, request=None):
        """ Fonction appellée par freeradius. Enregistre la mac pour
        une machine inconnue sur le compte de l'user"""
        allowed, _message, _rights = Machine.can_create(self, self.id)
        if not allowed:
            return False, _("Maximum number of registered machines reached.")
        if not nas_type:
            return False, _("Re2o doesn't know wich machine type to assign.")
        machine_type_cible = nas_type.machine_type
        try:
            machine_parent = Machine()
            machine_parent.user = self
            interface_cible = Interface()
            interface_cible.mac_address = mac_address
            interface_cible.machine_type = machine_type_cible
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
            return False, traceback.format_exc()
        return interface_cible, _("OK")

    def notif_auto_newmachine(self, interface):
        """Notification mail lorsque une machine est automatiquement
        ajoutée par le radius"""
        template = loader.get_template("users/email_auto_newmachine")
        context = {
            "nom": self.get_full_name(),
            "mac_address": interface.mac_address,
            "asso_name": AssoOption.get_cached_value("name"),
            "interface_name": interface.domain,
            "asso_email": AssoOption.get_cached_value("contact"),
            "pseudo": self.pseudo,
        }

        send_mail(
            None,
            "Ajout automatique d'une machine / New machine autoregistered",
            "",
            GeneralOption.get_cached_value("email_from"),
            [self.email],
            html_message=template.render(context),
        )
        return

    def notif_disable(self, request=None):
        """Envoi un mail de notification informant que l'adresse mail n'a pas été confirmée"""
        template = loader.get_template("users/email_disable_notif")
        context = {
            "name": self.get_full_name(),
            "asso_name": AssoOption.get_cached_value("name"),
            "asso_email": AssoOption.get_cached_value("contact"),
            "site_name": GeneralOption.get_cached_value("site_name"),
        }

        send_mail(
            request,
            "Suspension automatique / Automatic suspension",
            template.render(context),
            GeneralOption.get_cached_value("email_from"),
            [self.email],
            fail_silently=False,
        )
        return

    def set_password(self, password):
        """ A utiliser de préférence, set le password en hash courrant et
        dans la version ntlm"""
        from re2o.login import hashNT

        super().set_password(password)
        self.pwd_ntlm = hashNT(password)
        return

    def confirm_mail(self):
        """Marque l'email de l'utilisateur comme confirmé"""
        self.email_state = self.EMAIL_STATE_VERIFIED

    @cached_property
    def email_address(self):
        if (
            OptionalUser.get_cached_value("local_email_accounts_enabled")
            and self.local_email_enabled
        ):
            return self.emailaddress_set.all()
        return EMailAddress.objects.none()

    def get_next_domain_name(self):
        """Look for an available name for a new interface for
        this user by trying "pseudo0", "pseudo1", "pseudo2", ...

        Recherche un nom disponible, pour une machine. Doit-être
        unique, concatène le nom, le pseudo et le numero de machine
        """

        def simple_pseudo():
            """Renvoie le pseudo sans underscore (compat dns)"""
            return self.pseudo.replace("_", "-").lower()

        def composed_pseudo(name):
            """Renvoie le resultat de simplepseudo et rajoute le nom"""
            return simple_pseudo() + str(name)

        num = 0
        while Domain.objects.filter(name=composed_pseudo(num)):
            num += 1
        return composed_pseudo(num)

    def can_edit(self, user_request, *_args, **_kwargs):
        """Check if a user can edit a user object.

        :param self: The user which is to be edited.
        :param user_request: The user who requests to edit self.
        :return: a message and a boolean which is True if self is a club and
            user_request one of its member, or if user_request is self, or if
            user_request has the 'cableur' right.
        """
        if self.state in (self.STATE_ARCHIVE, self.STATE_FULL_ARCHIVE):
            warning_message = _("This user is archived.")
        else:
            warning_message = None

        if self.is_class_club and user_request.is_class_adherent:
            if (
                self == user_request
                or user_request.has_perm("users.change_user")
                or user_request.adherent in self.club.administrators.all()
            ):
                return True, warning_message, None
            else:
                return (
                    False,
                    _("You don't have the right to edit this club."),
                    ("users.change_user",),
                )
        else:
            if self == user_request:
                return True, warning_message, None
            elif user_request.has_perm("users.change_all_users"):
                return True, warning_message, None
            elif user_request.has_perm("users.change_user"):
                if self.groups.filter(listright__critical=True):
                    return (
                        False,
                        _("User with critical rights, can't be edited."),
                        ("users.change_all_users",),
                    )
                elif self == AssoOption.get_cached_value("utilisateur_asso"):
                    return (
                        False,
                        _(
                            "Impossible to edit the organisation's"
                            " user without the \"change_all_users\" right."
                        ),
                        ("users.change_all_users",),
                    )
                else:
                    return True, warning_message, None
            elif user_request.has_perm("users.change_all_users"):
                return True, warning_message, None
            else:
                return (
                    False,
                    _("You don't have the right to edit another user."),
                    ("users.change_user", "users.change_all_users"),
                )

    def can_change_password(self, user_request, *_args, **_kwargs):
        """Check if a user can change a user's password

        :param self: The user which is to be edited
        :param user_request: The user who request to edit self
        :returns: a message and a boolean which is True if self is a club
            and user_request one of it's admins, or if user_request is self,
            or if user_request has the right to change other's password
        """
        if self.is_class_club and user_request.is_class_adherent:
            if (
                self == user_request
                or user_request.has_perm("users.change_user_password")
                or user_request.adherent in self.club.administrators.all()
            ):
                return True, None, None
            else:
                return (
                    False,
                    _("You don't have the right to edit this club."),
                    ("users.change_user_password",),
                )
        else:
            if self == user_request or user_request.has_perm(
                "users.change_user_groups"
            ):
                # Peut éditer les groupes d'un user,
                # c'est un privilège élevé, True
                return True, None, None
            elif user_request.has_perm("users.change_user") and not self.groups.all():
                return True, None, None
            else:
                return (
                    False,
                    _("You don't have the right to edit another user."),
                    ("users.change_user_groups", "users.change_user"),
                )

    def check_selfpasswd(self, user_request, *_args, **_kwargs):
        """ Returns (True, None, None) if user_request is self, else returns
        (False, None, None)
        """
        return user_request == self, None, None

    def can_change_room(self, user_request, *_args, **_kwargs):
        """ Check if a user can change a room

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a state
        """
        if not (
            (
                self.pk == user_request.pk
                and OptionalUser.get_cached_value("self_room_policy") != OptionalUser.DISABLED
            )
            or user_request.has_perm("users.change_user")
        ):
            return (
                False,
                _("You don't have the right to change the room."),
                ("users.change_user",),
            )
        else:
            return True, None, None

    @staticmethod
    def can_change_state(user_request, *_args, **_kwargs):
        """ Check if a user can change a state

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a state
        """
        can = user_request.has_perm("users.change_user_state")
        return (
            can,
            _("You don't have the right to change the state.") if not can else None,
            ("users.change_user_state",),
        )

    def can_change_shell(self, user_request, *_args, **_kwargs):
        """ Check if a user can change a shell

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a shell
        """
        if not (
            (
                self.pk == user_request.pk
                and OptionalUser.get_cached_value("self_change_shell")
            )
            or user_request.has_perm("users.change_user_shell")
        ):
            return (
                False,
                _("You don't have the right to change the shell."),
                ("users.change_user_shell",),
            )
        else:
            return True, None, None

    @staticmethod
    def can_change_local_email_redirect(user_request, *_args, **_kwargs):
        """ Check if a user can change local_email_redirect.

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a redirection
        """
        can = OptionalUser.get_cached_value("local_email_accounts_enabled")
        return (
            can,
            _("Local email accounts must be enabled.") if not can else None,
            None,
        )

    @staticmethod
    def can_change_local_email_enabled(user_request, *_args, **_kwargs):
        """ Check if a user can change internal address.

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change internal address
        """
        can = OptionalUser.get_cached_value("local_email_accounts_enabled")
        return (
            can,
            _("Local email accounts must be enabled.") if not can else None,
            None,
        )

    @staticmethod
    def can_change_force(user_request, *_args, **_kwargs):
        """ Check if a user can change a force

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a force
        """
        can = user_request.has_perm("users.change_user_force")
        return (
            can,
            _("You don't have the right to force the move.") if not can else None,
            ("users.change_user_force",),
        )

    @staticmethod
    def can_change_groups(user_request, *_args, **_kwargs):
        """ Check if a user can change a group

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a group
        """
        can = user_request.has_perm("users.change_user_groups")
        return (
            can,
            _("You don't have the right to edit the user's groups of rights.")
            if not can
            else None,
            ("users.change_user_groups"),
        )

    @staticmethod
    def can_change_is_superuser(user_request, *_args, **_kwargs):
        """ Check if an user can change a is_superuser flag

        :param user_request: The user who request
        :returns: a message and a boolean which is True if permission is granted.
        """
        can = user_request.is_superuser
        return (
            can,
            _("\"superuser\" right required to edit the superuser flag.")
            if not can
            else None,
            [],
        )

    def can_view(self, user_request, *_args, **_kwargs):
        """Check if an user can view an user object.

        :param self: The targeted user.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
            text
        """
        if self.is_class_club and user_request.is_class_adherent:
            if (
                self == user_request
                or user_request.has_perm("users.view_user")
                or user_request.adherent in self.club.administrators.all()
                or user_request.adherent in self.club.members.all()
            ):
                return True, None, None
            else:
                return (
                    False,
                    _("You don't have the right to view this club."),
                    ("users.view_user",),
                )
        else:
            if self == user_request or user_request.has_perm("users.view_user"):
                return True, None, None
            else:
                return (
                    False,
                    _("You don't have the right to view another user."),
                    ("users.view_user",),
                )

    @staticmethod
    def can_view_all(user_request, *_args, **_kwargs):
        """Check if an user can access to the list of every user objects

        :param user_request: The user who wants to view the list.
        :return: True if the user can view the list and an explanation
            message.
        """
        can = user_request.has_perm("users.view_user")
        return (
            can,
            _("You don't have the right to view the list of users.")
            if not can
            else None,
            ("users.view_user",),
        )

    def can_delete(self, user_request, *_args, **_kwargs):
        """Check if an user can delete an user object.

        :param self: The user who is to be deleted.
        :param user_request: The user who requests deletion.
        :return: True if user_request has the right 'bureau', and a
            message.
        """
        can = user_request.has_perm("users.delete_user")
        return (
            can,
            _("You don't have the right to delete this user.") if not can else None,
            ("users.delete_user",),
        )

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.field_permissions = {
            "shell": self.can_change_shell,
            "force": self.can_change_force,
            "selfpasswd": self.check_selfpasswd,
            "local_email_redirect": self.can_change_local_email_redirect,
            "local_email_enabled": self.can_change_local_email_enabled,
            "room": self.can_change_room,
        }
        self.__original_state = self.state
        self.__original_email = self.email

    def clean_pseudo(self, *args, **kwargs):
        if EMailAddress.objects.filter(local_part=self.pseudo.lower()).exclude(
            user_id=self.id
        ):
            raise ValidationError(_("This username is already used."))

    def clean_email(self, *args, **kwargs):
        # Allow empty emails only if the user had an empty email before
        is_created = not self.pk
        if not self.email and (self.__original_email or is_created):
            raise forms.ValidationError(
                _("Email field cannot be empty.")
            )

        self.email = self.email.lower()

        if OptionalUser.get_cached_value("local_email_domain") in self.email:
            raise forms.ValidationError(
                _("You can't use a {} address as an external contact address.").format(
                    OptionalUser.get_cached_value("local_email_domain")
                )
            )

    def clean(self, *args, **kwargs):
        """Check if this pseudo is already used by any mailalias.
        Better than raising an error in post-save and catching it"""
        super(User, self).clean(*args, **kwargs)
        self.clean_pseudo(*args, **kwargs)
        self.clean_email(*args, **kwargs)

    def __str__(self):
        return self.pseudo


class Adherent(User):
    """ A class representing a member (it's a user with special
    informations) """

    name = models.CharField(max_length=255)
    room = models.OneToOneField(
        "topologie.Room", on_delete=models.PROTECT, blank=True, null=True
    )
    gpg_fingerprint = models.CharField(max_length=49, blank=True, null=True)

    class Meta(User.Meta):
        verbose_name = _("member")
        verbose_name_plural = _("members")

    def format_gpgfp(self):
        """Format gpg finger print as AAAA BBBB... from a string AAAABBBB...."""
        self.gpg_fingerprint = " ".join(
            [
                self.gpg_fingerprint[i : i + 4]
                for i in range(0, len(self.gpg_fingerprint), 4)
            ]
        )

    def validate_gpgfp(self):
        """Validate from raw entry if is it a valid gpg fp"""
        if self.gpg_fingerprint:
            gpg_fingerprint = self.gpg_fingerprint.replace(" ", "").upper()
            if not re.match("^[0-9A-F]{40}$", gpg_fingerprint):
                raise ValidationError(
                    _("A GPG fingerprint must contain 40 hexadecimal characters.")
                )
            self.gpg_fingerprint = gpg_fingerprint

    @classmethod
    def get_instance(cls, adherentid, *_args, **_kwargs):
        """Try to find an instance of `Adherent` with the given id.

        :param adherentid: The id of the adherent we are looking for.
        :return: An adherent.
        """
        return cls.objects.get(pk=adherentid)

    @staticmethod
    def can_create(user_request, *_args, **_kwargs):
        """Check if an user can create an user object.

        :param user_request: The user who wants to create a user object.
        :return: a message and a boolean which is True if the user can create
            a user or if the `options.all_can_create` is set.
        """
        if not user_request.is_authenticated:
            if not OptionalUser.get_cached_value(
                "self_adhesion"
            ):
                return False, _("Self registration is disabled."), None
            else:
                return True, None, None
        else:
            if OptionalUser.get_cached_value("all_can_create_adherent"): 
                return True, None, None
            else:
                can = user_request.has_perm("users.add_user")
                return (
                    can,
                    _("You don't have the right to create a user.")
                    if not can
                    else None,
                    ("users.add_user",),
                )

    def clean(self, *args, **kwargs):
        """Format the GPG fingerprint"""
        super(Adherent, self).clean(*args, **kwargs)
        if self.gpg_fingerprint:
            self.validate_gpgfp()
            self.format_gpgfp()


class Club(User):
    """ A class representing a club (it is considered as a user
    with special informations) """

    room = models.ForeignKey(
        "topologie.Room", on_delete=models.PROTECT, blank=True, null=True
    )
    administrators = models.ManyToManyField(
        blank=True, to="users.Adherent", related_name="club_administrator"
    )
    members = models.ManyToManyField(
        blank=True, to="users.Adherent", related_name="club_members"
    )
    mailing = models.BooleanField(default=False)

    class Meta(User.Meta):
        verbose_name = _("club")
        verbose_name_plural = _("clubs")

    @staticmethod
    def can_create(user_request, *_args, **_kwargs):
        """Check if an user can create an user object.

        :param user_request: The user who wants to create a user object.
        :return: a message and a boolean which is True if the user can create
            an user or if the `options.all_can_create` is set.
        """
        if not user_request.is_authenticated:
            return False, _("You must be authenticated."), None
        else:
            if OptionalUser.get_cached_value("all_can_create_club"):
                return True, None, None
            else:
                can = user_request.has_perm("users.add_user")
                return (
                    can,
                    _("You don't have the right to create a club.")
                    if not can
                    else None,
                    ("users.add_user",),
                )

    @staticmethod
    def can_view_all(user_request, *_args, **_kwargs):
        """Check if an user can access to the list of every user objects

        :param user_request: The user who wants to view the list.
        :return: True if the user can view the list and an explanation
            message.
        """
        if user_request.has_perm("users.view_user"):
            return True, None, None
        if (
            hasattr(user_request, "is_class_adherent")
            and user_request.is_class_adherent
        ):
            if (
                user_request.adherent.club_administrator.all()
                or user_request.adherent.club_members.all()
            ):
                return True, None, None
        return (
            False,
            _("You don't have the right to view the list of users."),
            ("users.view_user",),
        )

    @classmethod
    def get_instance(cls, clubid, *_args, **_kwargs):
        """Try to find an instance of `Club` with the given id.

        :param clubid: The id of the adherent we are looking for.
        :return: A club.
        """
        return cls.objects.get(pk=clubid)


@receiver(post_save, sender=Adherent)
@receiver(post_save, sender=Club)
@receiver(post_save, sender=User)
def user_post_save(**kwargs):
    """ Synchronisation post_save : envoie le mail de bienvenue si creation
    Synchronise le pseudo, en créant un alias mail correspondant
    Synchronise le ldap"""
    is_created = kwargs["created"]
    user = kwargs["instance"]
    EMailAddress.objects.get_or_create(local_part=user.pseudo.lower(), user=user)

    if is_created:
        user.notif_inscription(user.request)

    user.state_sync()
    user.ldap_sync(
        base=True, access_refresh=True, mac_refresh=False, group_refresh=True
    )
    regen("mailing")


@receiver(m2m_changed, sender=User.groups.through)
def user_group_relation_changed(**kwargs):
    action = kwargs["action"]
    if action in ("post_add", "post_remove", "post_clear"):
        user = kwargs["instance"]
        user.ldap_sync(
            base=False, access_refresh=False, mac_refresh=False, group_refresh=True
        )


@receiver(post_delete, sender=Adherent)
@receiver(post_delete, sender=Club)
@receiver(post_delete, sender=User)
def user_post_delete(**kwargs):
    """Post delete d'un user, on supprime son instance ldap"""
    user = kwargs["instance"]
    user.ldap_del()
    regen("mailing")


class ServiceUser(RevMixin, AclMixin, AbstractBaseUser):
    """ Classe des users daemons, règle leurs accès au ldap"""

    readonly = "readonly"
    ACCESS = (("auth", "auth"), ("readonly", "readonly"), ("usermgmt", "usermgmt"))

    pseudo = models.CharField(
        max_length=32,
        unique=True,
        help_text=_("Must only contain letters, numerals or dashes."),
        validators=[linux_user_validator],
    )
    access_group = models.CharField(choices=ACCESS, default=readonly, max_length=32)
    comment = models.CharField(help_text=_("Comment."), max_length=255, blank=True)

    USERNAME_FIELD = "pseudo"
    objects = UserManager()

    class Meta:
        permissions = (("view_serviceuser", _("Can view a service user object")),)
        verbose_name = _("service user")
        verbose_name_plural = _("service users")

    def get_full_name(self):
        """ Renvoie le nom complet du serviceUser formaté nom/prénom"""
        return _("Service user <{name}>").format(name=self.pseudo)

    def get_short_name(self):
        """ Renvoie seulement le nom"""
        return self.pseudo

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
        group.members = list(
            LdapServiceUser.objects.filter(
                name__in=[
                    user.pseudo
                    for user in ServiceUser.objects.filter(
                        access_group=self.access_group
                    )
                ]
            ).values_list("dn", flat=True)
        )
        group.save()

    def __str__(self):
        return self.pseudo


@receiver(post_save, sender=ServiceUser)
def service_user_post_save(**kwargs):
    """ Synchronise un service user ldap après modification django"""
    service_user = kwargs["instance"]
    service_user.ldap_sync()


@receiver(post_delete, sender=ServiceUser)
def service_user_post_delete(**kwargs):
    """ Supprime un service user ldap après suppression django"""
    service_user = kwargs["instance"]
    service_user.ldap_del()


class School(RevMixin, AclMixin, models.Model):
    """ Etablissement d'enseignement"""

    name = models.CharField(max_length=255)

    class Meta:
        permissions = (("view_school", _("Can view a school object")),)
        verbose_name = _("school")
        verbose_name_plural = _("schools")

    def __str__(self):
        return self.name


class ListRight(RevMixin, AclMixin, Group):
    """ Ensemble des droits existants. Chaque droit crée un groupe
    ldap synchronisé, avec gid.
    Permet de gérer facilement les accès serveurs et autres
    La clef de recherche est le gid, pour cette raison là
    il n'est plus modifiable après creation"""

    unix_name = models.CharField(
        max_length=255,
        unique=True,
        validators=[
            RegexValidator(
                "^[a-z]+$",
                message=(_("UNIX group names can only contain lower case letters.")),
            )
        ],
    )
    gid = models.PositiveIntegerField(unique=True, null=True)
    critical = models.BooleanField(default=False)
    details = models.CharField(help_text=_("Description."), max_length=255, blank=True)

    class Meta:
        permissions = (("view_listright", _("Can view a group of rights object")),)
        verbose_name = _("group of rights")
        verbose_name_plural = _("groups of rights")

    def __str__(self):
        return self.name

    def ldap_sync(self):
        """Sychronise les groups ldap avec le model listright coté django"""
        try:
            group_ldap = LdapUserGroup.objects.get(gid=self.gid)
        except LdapUserGroup.DoesNotExist:
            group_ldap = LdapUserGroup(gid=self.gid)
        group_ldap.name = self.unix_name
        group_ldap.members = [user.pseudo for user in self.user_set.all()]
        group_ldap.save()

    def ldap_del(self):
        """Supprime un groupe ldap"""
        try:
            group_ldap = LdapUserGroup.objects.get(gid=self.gid)
            group_ldap.delete()
        except LdapUserGroup.DoesNotExist:
            pass


@receiver(post_save, sender=ListRight)
def listright_post_save(**kwargs):
    """ Synchronise le droit ldap quand il est modifié"""
    right = kwargs["instance"]
    right.ldap_sync()


@receiver(post_delete, sender=ListRight)
def listright_post_delete(**kwargs):
    """Suppression d'un groupe ldap après suppression coté django"""
    right = kwargs["instance"]
    right.ldap_del()


class ListShell(RevMixin, AclMixin, models.Model):
    """Un shell possible. Pas de check si ce shell existe, les
    admin sont des grands"""

    shell = models.CharField(max_length=255, unique=True)

    class Meta:
        permissions = (("view_listshell", _("Can view a shell object")),)
        verbose_name = _("shell")
        verbose_name_plural = _("shells")

    def get_pretty_name(self):
        """Return the canonical name of the shell"""
        return self.shell.split("/")[-1]

    def __str__(self):
        return self.shell


class Ban(RevMixin, AclMixin, models.Model):
    """ Bannissement. Actuellement a un effet tout ou rien.
    Gagnerait à être granulaire"""

    STATE_HARD = 0
    STATE_SOFT = 1
    STATE_BRIDAGE = 2
    STATES = (
        (0, _("HARD (no access)")),
        (1, _("SOFT (local access only)")),
        (2, _("RESTRICTED (speed limitation)")),
    )

    user = models.ForeignKey("User", on_delete=models.PROTECT)
    raison = models.CharField(max_length=255)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField()
    state = models.IntegerField(choices=STATES, default=STATE_HARD)
    request = None

    class Meta:
        permissions = (("view_ban", _("Can view a ban object")),)
        verbose_name = _("ban")
        verbose_name_plural = _("bans")

    def notif_ban(self, request=None):
        """ Prend en argument un objet ban, envoie un mail de notification """
        template = loader.get_template("users/email_ban_notif")
        context = {
            "name": self.user.get_full_name(),
            "raison": self.raison,
            "date_end": self.date_end,
            "asso_name": AssoOption.get_cached_value("name"),
        }

        send_mail(
            request,
            "Déconnexion disciplinaire / Disciplinary disconnection",
            template.render(context),
            GeneralOption.get_cached_value("email_from"),
            [self.user.email],
            fail_silently=False,
        )
        return

    def is_active(self):
        """Ce ban est-il actif?"""
        return self.date_end > timezone.now()

    def can_view(self, user_request, *_args, **_kwargs):
        """Check if an user can view a Ban object.

        :param self: The targeted object.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
        text
        """
        if not user_request.has_perm("users.view_ban") and self.user != user_request:
            return (
                False,
                _("You don't have the right to view other bans than yours."),
                ("users.view_ban",),
            )
        else:
            return True, None, None

    def __str__(self):
        return str(self.user) + " " + str(self.raison)


@receiver(post_save, sender=Ban)
def ban_post_save(**kwargs):
    """ Regeneration de tous les services après modification d'un ban"""
    ban = kwargs["instance"]
    is_created = kwargs["created"]
    user = ban.user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    regen("mailing")
    if is_created:
        ban.notif_ban(ban.request)
        regen("dhcp")
        regen("mac_ip_list")
    if user.has_access():
        regen("dhcp")
        regen("mac_ip_list")


@receiver(post_delete, sender=Ban)
def ban_post_delete(**kwargs):
    """ Regen de tous les services après suppression d'un ban"""
    user = kwargs["instance"].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    regen("mailing")
    regen("dhcp")
    regen("mac_ip_list")


class Whitelist(RevMixin, AclMixin, models.Model):
    """Accès à titre gracieux. L'utilisateur ne paye pas; se voit
    accorder un accès internet pour une durée défini. Moins
    fort qu'un ban quel qu'il soit"""

    user = models.ForeignKey("User", on_delete=models.PROTECT)
    raison = models.CharField(max_length=255)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField()

    class Meta:
        permissions = (("view_whitelist", _("Can view a whitelist object")),)
        verbose_name = _("whitelist (free of charge access)")
        verbose_name_plural = _("whitelists (free of charge access)")

    def is_active(self):
        """ Is this whitelisting active ? """
        return self.date_end > timezone.now()

    def can_view(self, user_request, *_args, **_kwargs):
        """Check if an user can view a Whitelist object.

        :param self: The targeted object.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
        text
        """
        if (
            not user_request.has_perm("users.view_whitelist")
            and self.user != user_request
        ):
            return (
                False,
                _("You don't have the right to view other whitelists than yours."),
                ("users.view_whitelist",),
            )
        else:
            return True, None, None

    def __str__(self):
        return str(self.user) + " " + str(self.raison)


@receiver(post_save, sender=Whitelist)
def whitelist_post_save(**kwargs):
    """Après modification d'une whitelist, on synchronise les services
    et on lui permet d'avoir internet"""
    whitelist = kwargs["instance"]
    user = whitelist.user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    is_created = kwargs["created"]
    regen("mailing")
    if is_created:
        regen("dhcp")
        regen("mac_ip_list")
    if user.has_access():
        regen("dhcp")
        regen("mac_ip_list")


@receiver(post_delete, sender=Whitelist)
def whitelist_post_delete(**kwargs):
    """Après suppression d'une whitelist, on supprime l'accès internet
    en forçant la régénration"""
    user = kwargs["instance"].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    regen("mailing")
    regen("dhcp")
    regen("mac_ip_list")


class Request(models.Model):
    """ Objet request, générant une url unique de validation.
    Utilisé par exemple pour la generation du mot de passe et
    sa réinitialisation"""

    PASSWD = "PW"
    EMAIL = "EM"
    TYPE_CHOICES = ((PASSWD, _("Password")), (EMAIL, _("Email address")))
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    token = models.CharField(max_length=32)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    expires_at = models.DateTimeField()

    def save(self):
        if not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(
                hours=GeneralOption.get_cached_value("req_expire_hrs")
            )
        if not self.token:
            self.token = str(uuid.uuid4()).replace("-", "")  # remove hyphens
        super(Request, self).save()


class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """

    # LDAP meta-data
    base_dn = LDAP["base_user_dn"]
    object_classes = [
        "inetOrgPerson",
        "top",
        "posixAccount",
        "sambaSamAccount",
        "radiusprofile",
        "shadowAccount",
    ]

    # attributes
    gid = ldapdb.models.fields.IntegerField(db_column="gidNumber")
    name = ldapdb.models.fields.CharField(
        db_column="cn", max_length=200, primary_key=True
    )
    uid = ldapdb.models.fields.CharField(db_column="uid", max_length=200)
    uidNumber = ldapdb.models.fields.IntegerField(db_column="uidNumber", unique=True)
    sn = ldapdb.models.fields.CharField(db_column="sn", max_length=200)
    login_shell = ldapdb.models.fields.CharField(
        db_column="loginShell", max_length=200, blank=True, null=True
    )
    mail = ldapdb.models.fields.CharField(db_column="mail", max_length=200)
    given_name = ldapdb.models.fields.CharField(db_column="givenName", max_length=200)
    home_directory = ldapdb.models.fields.CharField(
        db_column="homeDirectory", max_length=200
    )
    display_name = ldapdb.models.fields.CharField(
        db_column="displayName", max_length=200, blank=True, null=True
    )
    dialupAccess = ldapdb.models.fields.CharField(db_column="dialupAccess")
    sambaSID = ldapdb.models.fields.IntegerField(db_column="sambaSID", unique=True)
    user_password = ldapdb.models.fields.CharField(
        db_column="userPassword", max_length=200, blank=True, null=True
    )
    sambat_nt_password = ldapdb.models.fields.CharField(
        db_column="sambaNTPassword", max_length=200, blank=True, null=True
    )
    macs = ldapdb.models.fields.ListField(
        db_column="radiusCallingStationId", max_length=200, blank=True, null=True
    )
    shadowexpire = ldapdb.models.fields.CharField(
        db_column="shadowExpire", blank=True, null=True
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
    base_dn = LDAP["base_usergroup_dn"]
    object_classes = ["posixGroup"]

    # attributes
    gid = ldapdb.models.fields.IntegerField(db_column="gidNumber")
    members = ldapdb.models.fields.ListField(db_column="memberUid", blank=True)
    name = ldapdb.models.fields.CharField(
        db_column="cn", max_length=200, primary_key=True
    )

    def __str__(self):
        return self.name


class LdapServiceUser(ldapdb.models.Model):
    """
    Class for representing an LDAP userservice entry.

    Un user de service coté ldap
    """

    # LDAP meta-data
    base_dn = LDAP["base_userservice_dn"]
    object_classes = ["applicationProcess", "simpleSecurityObject"]

    # attributes
    name = ldapdb.models.fields.CharField(
        db_column="cn", max_length=200, primary_key=True
    )
    user_password = ldapdb.models.fields.CharField(
        db_column="userPassword", max_length=200, blank=True, null=True
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
    base_dn = LDAP["base_userservicegroup_dn"]
    object_classes = ["groupOfNames"]

    # attributes
    name = ldapdb.models.fields.CharField(
        db_column="cn", max_length=200, primary_key=True
    )
    members = ldapdb.models.fields.ListField(db_column="member", blank=True)

    def __str__(self):
        return self.name


class EMailAddress(RevMixin, AclMixin, models.Model):
    """Defines a local email account for a user
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text=_("User of the local email account.")
    )
    local_part = models.CharField(
        unique=True, max_length=128, help_text=_("Local part of the email address.")
    )

    class Meta:
        permissions = (
            ("view_emailaddress", _("Can view a local email account object")),
        )
        verbose_name = _("local email account")
        verbose_name_plural = _("local email accounts")

    def __str__(self):
        return str(self.local_part) + OptionalUser.get_cached_value(
            "local_email_domain"
        )

    @cached_property
    def complete_email_address(self):
        return str(self.local_part) + OptionalUser.get_cached_value(
            "local_email_domain"
        )

    @staticmethod
    def can_create(user_request, userid, *_args, **_kwargs):
        """Check if a user can create a `EMailAddress` object.

        Args:
            user_request: The user who wants to create the object.
            userid: The id of the user to whom the account is to be created

        Returns:
            a message and a boolean which is True if the user can create
            a local email account.
        """
        if user_request.has_perm("users.add_emailaddress"):
            return True, None, None
        if not OptionalUser.get_cached_value("local_email_accounts_enabled"):
            return (False, _("The local email accounts are not enabled."), None)
        if int(user_request.id) != int(userid):
            return (
                False,
                _(
                    "You don't have the right to add a local email"
                    " account to another user."
                ),
                ("users.add_emailaddress",),
            )
        elif user_request.email_address.count() >= OptionalUser.get_cached_value(
            "max_email_address"
        ):
            return (
                False,
                _("You reached the limit of {} local email accounts.").format(
                    OptionalUser.get_cached_value("max_email_address")
                ),
                None,
            )
        return True, None, None

    def can_view(self, user_request, *_args, **_kwargs):
        """Check if a user can view the local email account

        Args:
            user_request: The user who wants to view the object.

        Returns:
            a message and a boolean which is True if the user can see
            the local email account.
        """
        if user_request.has_perm("users.view_emailaddress"):
            return True, None, None
        if not OptionalUser.get_cached_value("local_email_accounts_enabled"):
            return (False, _("The local email accounts are not enabled."), None)
        if user_request == self.user:
            return True, None, None
        return (
            False,
            _(
                "You don't have the right to view another user's local"
                " email account."
            ),
            ("users.view_emailaddress",),
        )

    def can_delete(self, user_request, *_args, **_kwargs):
        """Check if a user can delete the alias

        Args:
            user_request: The user who wants to delete the object.

        Returns:
            a message and a boolean which is True if the user can delete
            the local email account.
        """
        if self.local_part == self.user.pseudo.lower():
            return (
                False,
                _(
                    "You can't delete a local email account whose"
                    " local part is the same as the username."
                ),
                None,
            )
        if user_request.has_perm("users.delete_emailaddress"):
            return True, None, None
        if not OptionalUser.get_cached_value("local_email_accounts_enabled"):
            return False, _("The local email accounts are not enabled."), None
        if user_request == self.user:
            return True, None, None
        return (
            False,
            _(
                "You don't have the right to delete another user's"
                " local email account."
            ),
            ("users.delete_emailaddress",),
        )

    def can_edit(self, user_request, *_args, **_kwargs):
        """Check if a user can edit the alias

        Args:
            user_request: The user who wants to edit the object.

        Returns:
            a message and a boolean which is True if the user can edit
            the local email account.
        """
        if self.local_part == self.user.pseudo.lower():
            return (
                False,
                _(
                    "You can't edit a local email account whose local"
                    " part is the same as the username."
                ),
                None,
            )
        if user_request.has_perm("users.change_emailaddress"):
            return True, None, None
        if not OptionalUser.get_cached_value("local_email_accounts_enabled"):
            return False, _("The local email accounts are not enabled."), None
        if user_request == self.user:
            return True, None, None
        return (
            False,
            _(
                "You don't have the right to edit another user's local"
                " email account."
            ),
            ("users.change_emailaddress",),
        )

    def clean(self, *args, **kwargs):
        self.local_part = self.local_part.lower()
        if "@" in self.local_part or "+" in self.local_part:
            raise ValidationError(_("The local part must not contain @ or +."))
        result, reason = smtp_check(self.local_part)
        if result:
            raise ValidationError(reason)
        super(EMailAddress, self).clean(*args, **kwargs)
