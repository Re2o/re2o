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
The database models for the 'users' app of re2o.

The goal is to keep the main actions here, i.e. the 'clean' and 'save'
function are higly reposnsible for the changes, checking the coherence of the
data and the good behaviour in general for not breaking the database.

For further details on each of those models, see the documentation details for
each.

Here are defined the following django models :
    * Users : Adherent and Club (which inherit from Base User Abstract of django).
    * Whitelists
    * Bans
    * Schools (teaching structures)
    * Rights (Groups and ListRight)
    * ServiceUser (for ldap connexions)

Also define django-ldapdb models :
    * LdapUser
    * LdapGroup
    * LdapServiceUser

These objects are sync from django regular models as auxiliary models from
sql data into ldap.
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
from django.core.files.uploadedfile import InMemoryUploadedFile

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

from PIL import Image
from io import BytesIO
import sys

# General utilities

def linux_user_check(login):
    """Check if a login comply with unix base login policy

    Parameters:
        login (string): Login to check

    Returns:
        boolean: True if login comply with policy
    """
    UNIX_LOGIN_PATTERN = re.compile("^[a-z][a-z0-9-]*[$]?$")
    return UNIX_LOGIN_PATTERN.match(login)


def linux_user_validator(login):
    """Check if a login comply with unix base login policy, returns
    a standard Django ValidationError if login is not correct

    Parameters:
        login (string): Login to check

    Returns:
        ValidationError if login comply with policy
    """
    if not linux_user_check(login):
        raise forms.ValidationError(
            _("The username \"%(label)s\" contains forbidden characters."),
            params={"label": login},
        )


def get_fresh_user_uid():
    """Return a fresh unused uid.

    Returns:
        uid (int): The fresh uid available
    """
    uids = list(range(int(min(UID_RANGES["users"])), int(max(UID_RANGES["users"]))))
    try:
        used_uids = list(User.objects.values_list("uid_number", flat=True))
    except:
        used_uids = []
    free_uids = [id for id in uids if id not in used_uids]
    return min(free_uids)


def get_fresh_gid():
    """Return a fresh unused gid.

    Returns:
        uid (int): The fresh gid available
    """
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
    """Base re2o User model

    Attributes:
        surname: surname of the user
        pseudo: login of the user
        email: The main email of the user
        local_email_redirect: Option for redirection of all emails to the main email
        local_email_enabled: If True, enable a local email account
        school: Optional field, the school of the user
        shell: User shell linux
        comment: Optionnal comment field
        pwd_ntlm: Hash password in ntlm for freeradius
        state: State of the user, can be active, not yet active, etc (see below)
        email_state: State of the main email (if confirmed or not)
        registered: Date of initial creation
        telephone: Phone number
        uid_number: Linux uid of this user
        legacy_uid: Optionnal legacy user id
        shortcuts_enabled : Option for js shortcuts
        email_change_date: Date of the last email change
        profile_image: Optionnal image profile
    """

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
        default=False,
        help_text=_("Enable the local email account.")
    )
    school = models.ForeignKey(
        "School",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text=_("Education institute.")
    )
    shell = models.ForeignKey(
        "ListShell",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text=_("Unix shell.")
    )
    comment = models.CharField(
        help_text=_("Comment, school year."), max_length=255, blank=True
    )
    pwd_ntlm = models.CharField(max_length=255)
    state = models.IntegerField(
        choices=STATES,
        default=STATE_NOT_YET_ACTIVE,
        help_text=_("Account state.")
    )
    email_state = models.IntegerField(choices=EMAIL_STATES, default=EMAIL_STATE_PENDING)
    registered = models.DateTimeField(auto_now_add=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    uid_number = models.PositiveIntegerField(default=get_fresh_user_uid, unique=True)
    legacy_uid = models.PositiveIntegerField(
        unique=True,
        blank=True,
        null=True,
        help_text=_("Optionnal legacy uid, for import and transition purpose")
    )
    shortcuts_enabled = models.BooleanField(
        verbose_name=_("enable shortcuts on Re2o website"), default=True
    )
    email_change_date = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='profile_image', blank=True)

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
            ("change_user_pseudo", _("Can edit the pseudo of a user")),
            (
                "change_user_groups",
                _("Can edit the groups of rights of a user (critical permission)"),
            ),
            ("change_all_users", _("Can edit all users, including those with rights")),
            ("view_user", _("Can view a user object")),
        )
        verbose_name = _("user (member or club)")
        verbose_name_plural = _("users (members or clubs)")

    ###### Shortcuts and methods for user instance ######

    @cached_property
    def name(self):
        """Shortcuts, returns name attribute if the user is linked with
        an adherent instance.

        Parameters:
            self (user instance): user to return infos

        Returns:
            name (string): Name value if available
        """
        if self.is_class_adherent:
            return self.adherent.name
        else:
            return ""

    @cached_property
    def room(self):
        """Shortcuts, returns room attribute; unique for adherent
        and multiple (queryset) for club.

        Parameters:
            self (user instance): user to return infos

        Returns:
            room (room instance): Room instance
        """
        if self.is_class_adherent:
            return self.adherent.room
        elif self.is_class_club:
            return self.club.room
        else:
            raise NotImplementedError(_("Unknown type."))

    @cached_property
    def get_mail_addresses(self):
        """Shortcuts, returns all local email address queryset only if local_email
        global option is enabled.

        Parameters:
            self (user instance): user to return infos

        Returns:
            emailaddresse_set (queryset): All Email address of the local account
        """
        if self.local_email_enabled:
            return self.emailaddress_set.all()
        return None

    @cached_property
    def get_mail(self):
        """Shortcuts, returns the email address to use to contact the instance user self.
        Depends on if local_email account has been activated, otherwise returns self.email.

        Parameters:
            self (user instance): user to return infos

        Returns:
            email (string): The correct email to use
        """
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
        """Shortcuts, returns the class string "Adherent" of "Club", related with the
        self instance.

        Parameters:
            self (user instance): user to return infos

        Returns:
            class (string): The class "Adherent" or "Club"
        """
        if hasattr(self, "adherent"):
            return "Adherent"
        elif hasattr(self, "club"):
            return "Club"
        else:
            raise NotImplementedError(_("Unknown type."))

    @cached_property
    def class_display(self):
        """Shortcuts, returns the pretty string "Member" of "Club", related with the
        self instance.

        Parameters:
            self (user instance): user to return infos

        Returns:
            class (string): "Member" or "Club"
        """
        if hasattr(self, "adherent"):
            return _("Member")
        elif hasattr(self, "club"):
            return _("Club")
        else:
            raise NotImplementedError(_("Unknown type."))

    @cached_property
    def gid_number(self):
        """Shortcuts, returns the main and default gid for users,
        from settings file

        Parameters:
            self (user instance): user to return infos

        Returns:
            gid (int): Default gid number
        """
        return int(LDAP["user_gid"])

    @cached_property
    def gid(self):
        """Shortcuts, returns the main and default gid for users,
        from settings file

        Parameters:
            self (user instance): user to return infos

        Returns:
            gid (int): Default gid number
        """
        return LDAP["user_gid"]

    @cached_property
    def is_class_club(self):
        """Shortcuts, returns if the instance related with user is
        a club.

        Parameters:
            self (user instance): user to return infos

        Returns:
            boolean : Returns true if this user is a club
        """
        return hasattr(self, "club")

    @cached_property
    def is_class_adherent(self):
        """Shortcuts, returns if the instance related with user is
        an adherent.

        Parameters:
            self (user instance): user to return infos

        Returns:
            boolean : Returns true if this user is an adherent
        """
        return hasattr(self, "adherent")

    @property
    def is_active(self):
        """Shortcuts, used by django for allowing connection from this user.
        Returns True if this user has state active, or not yet active,
        or if preferences allows connection for archived users.

        Parameters:
            self (user instance): user to return infos

        Returns:
            boolean : Returns true if this user is allow to connect.
        """
        allow_archived = OptionalUser.get_cached_value("allow_archived_connexion")
        return (
            self.state == self.STATE_ACTIVE
            or self.state == self.STATE_NOT_YET_ACTIVE
            or (
                allow_archived
                and self.state in (self.STATE_ARCHIVE, self.STATE_FULL_ARCHIVE)
            )
        )

    @property
    def is_staff(self):
        """Shortcuts, used by django for admin pannel access, shortcuts to
        is_admin.

        Parameters:
            self (user instance): user to return infos

        Returns:
            boolean : Returns true if this user is_staff.
        """
        return self.is_admin

    @property
    def is_admin(self):
        """Shortcuts, used by django for admin pannel access. Test if user
        instance is_superuser or member of admin group.

        Parameters:
            self (user instance): user to return infos

        Returns:
            boolean : Returns true if this user is allow to access to admin pannel.
        """
        admin, _ = Group.objects.get_or_create(name="admin")
        return self.is_superuser or admin in self.groups.all()

    def get_full_name(self):
        """Shortcuts, returns pretty full name to display both in case of user
        is a club or an adherent.

        Parameters:
            self (user instance): user to return infos

        Returns:
            full_name (string) : Returns full name, name + surname.
        """
        name = self.name
        if name:
            return "%s %s" % (name, self.surname)
        else:
            return self.surname

    def get_short_name(self):
        """Shortcuts, returns short name to display both in case of user is
        a club or an adherent.

        Parameters:
            self (user instance): user to return infos

        Returns:
            surname (string) : Returns surname.
        """
        return self.surname

    @property
    def get_shell(self):
        """Shortcuts, returns linux user shell to use for this user if
        provided, otherwise the default shell defined in preferences.

        Parameters:
            self (user instance): user to return infos

        Returns:
            shell (linux shell) : Returns linux shell.
        """
        return self.shell or OptionalUser.get_cached_value("shell_default")

    @cached_property
    def home_directory(self):
        """Shortcuts, returns linux user home directory to use.

        Parameters:
            self (user instance): user to return infos

        Returns:
            home dir (string) : Returns home directory.
        """
        return "/home/" + self.pseudo

    @cached_property
    def get_shadow_expire(self):
        """Shortcuts, returns the shadow expire value : 0 if this account is
        disabled or if the email has not been verified to block the account
        access.

        Parameters:
            self (user instance): user to return infos

        Returns:
            shadow_expire (int) : Shadow expire value.
        """
        if self.state == self.STATE_DISABLED or self.email_state == self.EMAIL_STATE_UNVERIFIED:
            return str(0)
        else:
            return None

    @cached_property
    def solde(self):
        """Shortcuts, calculate and returns the balance for this user, as a
        dynamic balance beetween debiti (-) and credit (+) "Vente" objects
        flaged as balance operations.

        Parameters:
            self (user instance): user to return infos

        Returns:
            solde (float) : The balance of the user.
        """
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

    @property
    def image_url(self):
        """Shortcuts, returns the url associated with the user profile_image,
        if an image has been set.

        Parameters:
            self (user instance): user to return infos

        Returns:
            profile_image_url (url) : Returns the url of this profile image.
        """
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url

    @cached_property
    def email_address(self):
        """Shortcuts, returns all the email addresses (queryset) associated
        with the local account, if the account has been activated,
        otherwise return a none queryset.

        Parameters:
            self (user instance): user to return infos

        Returns:
            email_address (django queryset) : Returns a queryset containing
            EMailAddress of this user.
        """
        if (
            OptionalUser.get_cached_value("local_email_accounts_enabled")
            and self.local_email_enabled
        ):
            return self.emailaddress_set.all()
        return EMailAddress.objects.none()

    def end_adhesion(self):
        """Methods, calculate and returns the end of membership value date of
        this user with aggregation of Cotisation objects linked to user
        instance.

        Parameters:
            self (user instance): user to return infos

        Returns:
            end_adhesion (date) : Date of the end of the membership.
        """
        date_max = (
            Cotisation.objects.filter(
                vente__in=Vente.objects.filter(
                    facture__in=Facture.objects.filter(user=self).exclude(valid=False)
                )
            )
            .aggregate(models.Max("date_end_memb"))["date_end_memb__max"]
        )
        return date_max

    def end_connexion(self):
        """Methods, calculate and returns the end of connection subscription value date
        of this user with aggregation of Cotisation objects linked to user instance.

        Parameters:
            self (user instance): user to return infos

        Returns:
            end_adhesion (date) : Date of the end of the connection subscription.
        """
        date_max = (
            Cotisation.objects.filter(
                vente__in=Vente.objects.filter(
                    facture__in=Facture.objects.filter(user=self).exclude(valid=False)
                )
            )
            .aggregate(models.Max("date_end_con"))["date_end_con__max"]
        )
        return date_max

    def is_adherent(self):
        """Methods, calculate and returns if the user has a valid membership by testing
        if end_adherent is after now or not.

        Parameters:
            self (user instance): user to return infos

        Returns:
            is_adherent (boolean) : True is user has a valid membership.
        """
        end = self.end_adhesion()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True
        # it looks wrong, we should check if there is a cotisation where 
        # were date_start_memb < timezone.now() < date_end_memb, 
        # in case the user purshased a cotisation starting in the futur
        # somehow

    def is_connected(self):
        """Methods, calculate and returns if the user has a valid membership AND a
        valid connection subscription by testing if end_connexion is after now or not.
        If true, returns is_adherent() method value.

        Parameters:
            self (user instance): user to return infos

        Returns:
            is_connected (boolean) : True is user has a valid membership and a valid connexion.
        """
        end = self.end_connexion()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return self.is_adherent()
        # it looks wrong, we should check if there is a cotisation where 
        # were date_start_con < timezone.now() < date_end_con, 
        # in case the user purshased a cotisation starting in the futur
        # somehow

    def end_ban(self):
        """Methods, calculate and returns the end of a ban value date
        of this user with aggregation of ban objects linked to user instance.

        Parameters:
            self (user instance): user to return infos

        Returns:
            end_ban (date) : Date of the end of the bans objects.
        """
        date_max = Ban.objects.filter(user=self).aggregate(models.Max("date_end"))[
            "date_end__max"
        ]
        return date_max

    def end_whitelist(self):
        """Methods, calculate and returns the end of a whitelist value date
        of this user with aggregation of whitelists objects linked to user instance.

        Parameters:
            self (user instance): user to return infos

        Returns:
            end_whitelist (date) : Date of the end of the whitelists objects.
        """
        date_max = Whitelist.objects.filter(user=self).aggregate(
            models.Max("date_end")
        )["date_end__max"]
        return date_max

    def is_ban(self):
        """Methods, calculate and returns if the user is banned by testing
        if end_ban is after now or not.

        parameters:
            self (user instance): user to return infos

        returns:
            is_ban (boolean) : true if user is under a ban sanction decision.
        """
        end = self.end_ban()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    def is_whitelisted(self):
        """Methods, calculate and returns if the user has a whitelist free connection
        if end_whitelist is after now or not.

        parameters:
            self (user instance): user to return infos

        returns:
            is_whitelisted (boolean) : true if user has a whitelist connection.
        """
        end = self.end_whitelist()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    def has_access(self):
        """Methods, returns if the user has an internet access.
        Return True if user is active and has a verified email, is not under a ban
        decision and has a valid membership and connection or a whitelist.

        parameters:
            self (user instance): user to return infos

        returns:
            has_access (boolean) : true if user has an internet connection.
        """
        return (
            self.state == User.STATE_ACTIVE
            and self.email_state != User.EMAIL_STATE_UNVERIFIED
            and not self.is_ban()
            and (self.is_connected() or self.is_whitelisted())
        ) or self == AssoOption.get_cached_value("utilisateur_asso")

    def end_access(self):
        """Methods, returns the date of the end of the connection for this user,
        as the maximum date beetween connection (membership objects) and whitelists.

        parameters:
            self (user instance): user to return infos

        returns:
            end_access (datetime) : Returns the date of the end_access connection.
        """
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

    @classmethod
    def users_interfaces(cls, users, active=True, all_interfaces=False):
        """Class method, returns all interfaces related/belonging to users
        contained in query_sert "users".

        Parameters:
            users (list of users queryset): users which interfaces
            have to be returned
            active (boolean): If true, filter on interfaces
            all_interfaces (boolean): If true, returns all interfaces

        returns:
            interfaces (queryset): Queryset of interfaces instances

        """
        if all_interfaces:
            return Interface.objects.filter(
                machine__in=Machine.objects.filter(user__in=users)
            ).select_related("domain__extension")
        else:
            return Interface.objects.filter(
                machine__in=Machine.objects.filter(user__in=users, active=active)
            ).select_related("domain__extension")

    def user_interfaces(self, active=True, all_interfaces=False):
        """Method, returns all interfaces related/belonging to an user.

        Parameters:
            self (user instance): user which interfaces
            have to be returned
            active (boolean): If true, filter on interfaces
            all_interfaces (boolean): If true, returns all interfaces

        returns:
            interfaces (queryset): Queryset of interfaces instances

        """
        return self.users_interfaces(
            [self], active=active, all_interfaces=all_interfaces
        )

    ###### Methods and user edition functions, modify user attributes ######

    def set_active(self):
        """Method, make this user active. Called in post-saved of subscription,
        set the state value active if state is not_yet_active, with
        a valid membership.
        Also make an archived user fully active.

        Parameters:
            self (user instance): user to set active

        """
        if self.state == self.STATE_NOT_YET_ACTIVE:
            if self.facture_set.filter(valid=True).filter(
                ~(Q(vente__duration_membership__isnull=True) | Q(vente__duration_membership=0)))\
                .filter(~(Q(vente__duration_days_membership__isnull=True) | Q(vente__duration_days_membership=0))
            ).exists() or OptionalUser.get_cached_value("all_users_active"):
                self.state = self.STATE_ACTIVE
                self.save()
        if self.state == self.STATE_ARCHIVE or self.state == self.STATE_FULL_ARCHIVE:
            self.state = self.STATE_ACTIVE
            self.unarchive()
            self.save()

    def set_password(self, password):
        """Method, overload the basic set_password inherited from django BaseUser.
        Called when setting a new password, to set the classic django password
        hashed, and also the NTLM hashed pwd_ntlm password.

        Parameters:
            self (user instance): user to set password
            password (string): new password (cleatext) to set.

        """
        from re2o.login import hashNT

        super().set_password(password)
        self.pwd_ntlm = hashNT(password)
        return

    def confirm_mail(self):
        """Method, set the email_state to VERIFIED when the email has been verified.

        Parameters:
            self (user instance): user to set password

        """
        self.email_state = self.EMAIL_STATE_VERIFIED

    def assign_ips(self):
        """Method, assigns ipv4 to all interfaces related to a user.

        Parameters:
            self (user instance): user which interfaces have to be assigned

        """
        interfaces = self.user_interfaces()
        with transaction.atomic(), reversion.create_revision():
            Interface.mass_assign_ipv4(interfaces)
            reversion.set_comment("IPv4 assignment")

    def unassign_ips(self):
        """Method, unassigns and remove ipv4 to all interfaces related to a user.
        (set ipv4 field to null)

        Parameters:
            self (user instance): user which interfaces have to be assigned

        """
        interfaces = self.user_interfaces()
        with transaction.atomic(), reversion.create_revision():
            Interface.mass_unassign_ipv4(interfaces)
            reversion.set_comment("IPv4 unassignment")

    @classmethod
    def mass_unassign_ips(cls, users_list):
        """Class method, unassigns and remove ipv4 to all interfaces related
        to a list of users.

        Parameters:
            users_list (list of users or queryset): users which interfaces
            have to be unassigned

        """
        interfaces = cls.users_interfaces(users_list)
        with transaction.atomic(), reversion.create_revision():
            Interface.mass_unassign_ipv4(interfaces)
            reversion.set_comment("IPv4 assignment")

    def disable_email(self):
        """Method, disable email account and email redirection for
        an user.

        Parameters:
            self (user instance): user to disabled email.

        """
        self.local_email_enabled = False
        self.local_email_redirect = False

    @classmethod
    def mass_disable_email(cls, queryset_users):
        """Class method, disable email accounts and email redirection for
        a list of users (or queryset).

        Parameters:
            users_list (list of users or queryset): users which email
            account to disable.

        """
        queryset_users.update(local_email_enabled=False)
        queryset_users.update(local_email_redirect=False)

    def delete_data(self):
        """Method, delete non mandatory data, delete machine,
        and disable email accounts for a list of users (or queryset).
        Called during full archive process.

        Parameters:
            self (user instance): user to delete data.

        """
        self.disable_email()
        self.machine_set.all().delete()

    @classmethod
    def mass_delete_data(cls, queryset_users):
        """Class method, delete non mandatory data, delete machine
        and disable email accounts for a list of users (or queryset).
        Called during full archive process.

        Parameters:
            users_list (list of users or queryset): users to perform
            delete data.

        """
        cls.mass_disable_email(queryset_users)
        Machine.mass_delete(Machine.objects.filter(user__in=queryset_users))
        cls.ldap_delete_users(queryset_users)

    def archive(self):
        """Method, archive user by unassigning ips.

        Parameters:
            self (user instance): user to archive.

        """
        self.unassign_ips()

    @classmethod
    def mass_archive(cls, users_list):
        """Class method, mass archive a queryset of users.
        Called during archive process, unassign ip and set to
        archive state.

        Parameters:
            users_list (list of users queryset): users to perform
            mass archive.

        """
        # Force eval of queryset
        bool(users_list)
        users_list = users_list.all()
        cls.mass_unassign_ips(users_list)
        users_list.update(state=User.STATE_ARCHIVE)

    def full_archive(self):
        """Method, full archive an user by unassigning ips, deleting data
        and ldap deletion.

        Parameters:
            self (user instance): user to full archive.

        """
        self.archive()
        self.delete_data()
        self.ldap_del()

    @classmethod
    def mass_full_archive(cls, users_list):
        """Class method, mass full archive a queryset of users.
        Called during full archive process, unassign ip, delete
        non mandatory data and set to full archive state.

        Parameters:
            users_list (list of users queryset): users to perform
            mass full archive.

        """
        # Force eval of queryset
        bool(users_list)
        users_list = users_list.all()
        cls.mass_unassign_ips(users_list)
        cls.mass_delete_data(users_list)
        users_list.update(state=User.STATE_FULL_ARCHIVE)

    def unarchive(self):
        """Method, unarchive an user by assigning ips, and recreating
        ldap user associated.

        Parameters:
            self (user instance): user to unarchive.

        """
        self.assign_ips()
        self.ldap_sync()

    def state_sync(self):
        """Master Method, call unarchive, full_archive or archive method
        on an user when state is changed, based on previous state.

        Parameters:
            self (user instance): user to sync state.

        """
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
        """Method ldap_sync, sync in ldap with self user attributes.
        Each User instance is copy into ldap, via a LdapUser virtual objects.
        This method performs a copy of several attributes (name, surname, mail,
        hashed SSHA password, ntlm password, shell, homedirectory).

        Update, or create if needed a ldap entry related with the User instance.

        Parameters:
            self (user instance): user to sync in ldap.
            base (boolean): Default true, if base is true, perform a basic
            sync of basic attributes.
            access_refresh (boolean): Default true, if access_refresh is true,
            update the dialup_access attributes based on has_access (is this user
            has a valid internet access).
            mac_refresh (boolean): Default true, if mac_refresh, update the mac_address
            list of the user.
            group_refresh (boolean): Default False, if true, update the groups membership
            of this user. Onerous option, call ldap_sync() on every groups of the user.

        """
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
        """Method, delete an user in ldap.

        Parameters:
            self (user instance): user to delete in Ldap.

        """
        try:
            user_ldap = LdapUser.objects.get(name=self.pseudo)
            user_ldap.delete()
        except LdapUser.DoesNotExist:
            pass

    @classmethod
    def ldap_delete_users(cls, queryset_users):
        """Class method, delete several users in ldap (queryset).

        Parameters:
            queryset_users (list of users queryset): users to delete
            in ldap.
        """
        LdapUser.objects.filter(
            name__in=list(queryset_users.values_list("pseudo", flat=True))
        )

    ###### Send mail functions ######

    def notif_inscription(self, request=None):
        """Method/function, send an email 'welcome' to user instance, after
        successfull register.

        Parameters:
            self (user instance): user to send the welcome email
            request (optional request): Specify request

        Returns:
            email: Welcome email after user register
        """
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
        """Method/function, makes a Request class instance, and send
        an email to user instance for password change in case of initial
        password set or forget password form.

        Parameters:
            self (user instance): user to send the welcome email
            request: Specify request, mandatory to build the reset link

        Returns:
            email: Reset password email for user instance
        """
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
        """Method/function, check if a confirmation by email is needed,
        and trigger send.
        * If the user changed email, it needs to be confirmed
        * If they're not fully archived, send a confirmation email

        Parameters:
            self (user instance): user to send the confirmation email
            request: Specify request, mandatory to build the reset link

        Returns:
            boolean: True if a confirmation of the mail is needed
        """
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
        """Method/function, update the value of the last email change,
        and call and send the confirm email link.
        Function called only after a manual of email_state by an admin.

        Parameters:
            self (user instance): user to send the confirmation email
            request: Specify request, mandatory to build the reset link

        Returns:
            boolean: True if a confirmation of the mail is needed
        """
        if self.email_state == self.EMAIL_STATE_VERIFIED:
            return False

        self.email_change_date = timezone.now()
        self.save()

        self.confirm_email_address_mail(request)
        return True

    def confirm_email_before_date(self):
        """Method/function, calculate the maximum date for confirmation
        of the new email address

        Parameters:
            self (user instance): user to calculate maximum date
            for confirmation

        Returns:
            date: Date of the maximum time to perform email confirmation
        """
        if self.email_state == self.EMAIL_STATE_VERIFIED:
            return None

        days = OptionalUser.get_cached_value("disable_emailnotyetconfirmed")
        return self.email_change_date + timedelta(days=days)

    def confirm_email_address_mail(self, request):
        """Method/function, makes a Request class instance, and send
        an email to user instance to confirm a new email address.
        * If the user changed email, it needs to be confirmed
        * If they're not fully archived, send a confirmation email

        Parameters:
            self (user instance): user to send the confirmation email
            request: Specify request, mandatory to build the reset link

        Returns:
            email: An email with a link to confirm the new email address
        """
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
        """Function, register a new interface on the user instance account.
        Called automaticaly mainly by freeradius python backend, for autoregister.

        Parameters:
            self (user instance): user to register new interface
            mac_address (string): New mac address to add on the new interface
            nas_type (Django Nas object instance): The nas object calling
            request: Optional django request

        Returns:
            interface (Interface instance): The new interface registered

        """
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
        """Function/method, send an email to notify the new interface
        registered on user instance account.

        Parameters:
            self (user instance): user to notify new registration
            interface (interface instance): new interface registered

        Returns:
            boolean: True if a confirmation of the mail is needed
        """
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
        """Function/method, send an email to notify that the account is disabled
        in case of unconfirmed email address.

        Parameters:
            self (user instance): user to notif disabled decision
            request (django request): request to build email

        Returns:
            email: Notification email
        """
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

    def get_next_domain_name(self):
        """Function/method, provide a unique name for a new interface.

        Parameters:
            self (user instance): user to get a new domain name

        Returns:
           domain name (string): String of new domain name
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

    def can_change_pseudo(self, user_request, *_args, **_kwargs):
        """ Check if a user can change a pseudo

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a shell
        """
        if not (
            (
                self.pk == user_request.pk
                and OptionalUser.get_cached_value("self_change_pseudo")
            )
            or user_request.has_perm("users.change_user_pseudo")
            or not self.pk
        ):
            return (
                False,
                _("You don't have the right to change the pseudo."),
                ("users.change_user_pseudo",),
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
            "pseudo": self.can_change_pseudo,
            "force": self.can_change_force,
            "selfpasswd": self.check_selfpasswd,
            "local_email_redirect": self.can_change_local_email_redirect,
            "local_email_enabled": self.can_change_local_email_enabled,
            "room": self.can_change_room,
        }
        self.__original_state = self.state
        self.__original_email = self.email

    def clean_pseudo(self, *args, **kwargs):
        """Method, clean the pseudo value. The pseudo must be unique, but also
        it must not already be used an an email address, so a check is performed.

        Parameters:
            self (user instance): user to clean pseudo value.

        Returns:
            Django ValidationError: if the pseudo value can not be used.

        """
        if EMailAddress.objects.filter(local_part=self.pseudo.lower()).exclude(
            user_id=self.id
        ):
            raise ValidationError(_("This username is already used."))

    def clean_email(self, *args, **kwargs):
        """Method, clean the email value.
        Validate that:
            * An email value has been provided; email field can't be nullified.
            (the user must be reachable by email)
            * The provided email is not a local email to avoid loops
            * Set the email as lower.

        Parameters:
            self (user instance): user to clean email value.

        Returns:
            Django ValidationError: if the email value can not be used.

        """
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
        """Method, general clean for User model.
        Clean pseudo and clean email.

        Parameters:
            self (user instance): user to clean.

        """
        super(User, self).clean(*args, **kwargs)
        self.clean_pseudo(*args, **kwargs)
        self.clean_email(*args, **kwargs)


    def save(self, *args, **kwargs):
        if self.profile_image:
            im = Image.open(self.profile_image)
            output = BytesIO()
            im = im.resize( (100,100) )
            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            im.save(output, format='JPEG', quality=100)
            output.seek(0)
            self.profile_image = InMemoryUploadedFile(output,'ImageField', "%s.jpg" %self.profile_image.name.split('.')[0], 'image/jpeg', sys.getsizeof(output), None)
        super(User,self).save(*args, **kwargs)

    def __str__(self):
        return self.pseudo


class Adherent(User):
    """Base re2o Adherent model, inherit from User. Add other attributes.

    Attributes:
        name: name of the user
        room: room of the user
        gpg_fingerprint: The gpgfp of the user

    """

    name = models.CharField(max_length=255)
    room = models.OneToOneField(
        "topologie.Room", on_delete=models.PROTECT, blank=True, null=True
    )
    gpg_fingerprint = models.CharField(max_length=49, blank=True, null=True)

    class Meta(User.Meta):
        verbose_name = _("member")
        verbose_name_plural = _("members")

    def format_gpgfp(self):
        """Method, format the gpgfp value, with blocks of 4 characters,
        as AAAA BBBB instead of AAAABBBB.

        Parameters:
            self (user instance): user to clean gpgfp value.

        """
        self.gpg_fingerprint = " ".join(
            [
                self.gpg_fingerprint[i : i + 4]
                for i in range(0, len(self.gpg_fingerprint), 4)
            ]
        )

    def validate_gpgfp(self):
        """Method, clean the gpgfp value, validate if the raw entry is a valid gpg fp.

        Parameters:
            self (user instance): user to clean gpgfp check.

        Returns:
            Django ValidationError: if the gpgfp value is invalid.

        """
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
        """Method, clean and validate the gpgfp value.

        Parameters:
            self (user instance): user to perform clean.

        """
        super(Adherent, self).clean(*args, **kwargs)
        if self.gpg_fingerprint:
            self.validate_gpgfp()
            self.format_gpgfp()


class Club(User):
    """ A class representing a club (it is considered as a user
    with special informations)

    Attributes:
        administrators: administrators of the club
        members: members of the club
        room: room(s) of the club
        mailing: Boolean, activate mailing list for this club.

    """

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
    """Django signal, post save operations on Adherent, Club and User.
    Sync pseudo, sync ldap, create mailalias and send welcome email if needed
    (new user)

    """
    is_created = kwargs["created"]
    user = kwargs["instance"]
    EMailAddress.objects.get_or_create(local_part=user.pseudo.lower(), user=user)

    if is_created:
        user.notif_inscription(user.request)
        user.set_active()
    user.state_sync()
    user.ldap_sync(
        base=True, access_refresh=True, mac_refresh=False, group_refresh=True
    )
    regen("mailing")


@receiver(m2m_changed, sender=User.groups.through)
def user_group_relation_changed(**kwargs):
    """Django signal, used for User Groups change (related models).
    Sync ldap, with calling group_refresh.

    """
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
    """Django signal, post delete operations on Adherent, Club and User.
    Delete user in ldap.

    """
    user = kwargs["instance"]
    user.ldap_del()
    regen("mailing")


class ServiceUser(RevMixin, AclMixin, AbstractBaseUser):
    """A class representing a serviceuser (it is considered as a user
    with special informations).
    The serviceuser is a special user used with special access to ldap tree. It is
    its only usefullness, and service user can't connect to re2o.
    Each service connected to ldap for auth (ex dokuwiki, owncloud, etc) should
    have a different service user with special acl (readonly, auth) and password.

    Attributes:
        pseudo: login of the serviceuser
        access_group: acl for this serviceuser
        comment: Comment for this serviceuser.

    """

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
        """Shortcuts, return a pretty name for the serviceuser.

        Parameters:
            self (ServiceUser instance): serviceuser to return infos.

        """
        return _("Service user <{name}>").format(name=self.pseudo)

    def get_short_name(self):
        """Shortcuts, return the shortname (pseudo) of the serviceuser.

        Parameters:
            self (ServiceUser instance): serviceuser to return infos.

        """
        return self.pseudo

    def ldap_sync(self):
        """Method ldap_sync, sync the serviceuser in ldap with its attributes.
        Each ServiceUser instance is copy into ldap, via a LdapServiceUser virtual object.
        This method performs a copy of several attributes (pseudo, access).

        Update, or create if needed a mirror ldap entry related with the ServiceUserinstance.

        Parameters:
            self (serviceuser instance): ServiceUser to sync in ldap.

        """
        try:
            user_ldap = LdapServiceUser.objects.get(name=self.pseudo)
        except LdapServiceUser.DoesNotExist:
            user_ldap = LdapServiceUser(name=self.pseudo)
        user_ldap.user_password = self.password[:6] + self.password[7:]
        user_ldap.save()
        self.serviceuser_group_sync()

    def ldap_del(self):
        """Method, delete an ServiceUser in ldap.

        Parameters:
            self (ServiceUser instance): serviceuser to delete in Ldap.

        """
        try:
            user_ldap = LdapServiceUser.objects.get(name=self.pseudo)
            user_ldap.delete()
        except LdapUser.DoesNotExist:
            pass
        self.serviceuser_group_sync()

    def serviceuser_group_sync(self):
        """Method, update serviceuser group sync in ldap.
        In LDAP, Acl depends on the ldapgroup (readonly, auth, or usermgt),
        so the ldap group need to be synced with the accessgroup field on ServiceUser.
        Called by ldap_sync and ldap_del.

        Parameters:
            self (ServiceUser instance): serviceuser to update groups in LDAP.

        """
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
    """Django signal, post save operations on ServiceUser.
    Sync or create serviceuser in ldap.

    """
    service_user = kwargs["instance"]
    service_user.ldap_sync()


@receiver(post_delete, sender=ServiceUser)
def service_user_post_delete(**kwargs):
    """Django signal, post delete operations on ServiceUser.
    Delete service user in ldap.

    """
    service_user = kwargs["instance"]
    service_user.ldap_del()


class School(RevMixin, AclMixin, models.Model):
    """A class representing a school; which users are linked.

    Attributes:
        name: name of the school

    """

    name = models.CharField(max_length=255)

    class Meta:
        permissions = (("view_school", _("Can view a school object")),)
        verbose_name = _("school")
        verbose_name_plural = _("schools")

    def __str__(self):
        return self.name


class ListRight(RevMixin, AclMixin, Group):
    """ A class representing a listright, inherit from basic django Group object.
    Each listrights/groups gathers several users, and can have individuals django
    rights, like can_view, can_edit, etc.
    Moreover, a ListRight is also a standard unix group, usefull for creating linux
    unix groups for servers access or re2o single rights, or both.
    Gid is used as a primary key, and can't be changed.

    Attributes:
        name: Inherited from Group, name of the ListRight
        gid: Group id unix
        critical: Boolean, if True the Group can't be changed without special acl
        details: Details and description of the group
    """

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
        """Method ldap_sync, sync the listright/group in ldap with its listright attributes.
        Each ListRight/Group instance is copy into ldap, via a LdapUserGroup virtual objects.
        This method performs a copy of several attributes (name, members, gid, etc).
        The primary key is the gid, and should never change.

        Update, or create if needed a ldap entry related with the ListRight/Group instance.

        Parameters:
            self (listright instance): ListRight/Group to sync in ldap.

        """
        try:
            group_ldap = LdapUserGroup.objects.get(gid=self.gid)
        except LdapUserGroup.DoesNotExist:
            group_ldap = LdapUserGroup(gid=self.gid)
        group_ldap.name = self.unix_name
        group_ldap.members = [user.pseudo for user in self.user_set.all()]
        group_ldap.save()

    def ldap_del(self):
        """Method, delete an ListRight/Group in ldap.

        Parameters:
            self (listright/Group instance): group to delete in Ldap.

        """
        try:
            group_ldap = LdapUserGroup.objects.get(gid=self.gid)
            group_ldap.delete()
        except LdapUserGroup.DoesNotExist:
            pass


@receiver(post_save, sender=ListRight)
def listright_post_save(**kwargs):
    """Django signal, post save operations on ListRight/Group objects.
    Sync or create group in ldap.

    """
    right = kwargs["instance"]
    right.ldap_sync()


@receiver(post_delete, sender=ListRight)
def listright_post_delete(**kwargs):
    """Django signal, post delete operations on ListRight/Group objects.
    Delete group in ldap.

    """
    right = kwargs["instance"]
    right.ldap_del()


class ListShell(RevMixin, AclMixin, models.Model):
    """A class representing a shell; which users are linked.
    A standard linux user shell. (zsh, bash, etc)

    Attributes:
        shell: name of the shell

    """

    shell = models.CharField(max_length=255, unique=True)

    class Meta:
        permissions = (("view_listshell", _("Can view a shell object")),)
        verbose_name = _("shell")
        verbose_name_plural = _("shells")

    def get_pretty_name(self):
        """Method, returns a pretty name for a shell like "bash" or "zsh".

        Parameters:
            self (listshell): Shell to return a pretty name.

        Returns:
           pretty_name (string): Return a pretty name string for this shell.

        """
        return self.shell.split("/")[-1]

    def __str__(self):
        return self.shell


class Ban(RevMixin, AclMixin, models.Model):
    """ A class representing a ban, which cuts internet access,
    as a sanction.

    Attributes:
        user: related user for this whitelist
        raison: reason of this ban, can be null
        date_start: Date of the start of the ban
        date_end: Date of the end of the ban
        state: Has no effect now, would specify this kind of ban
        (hard, soft)
    """

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
        """Function/method, send an email to notify that a ban has been
        decided and internet access disabled.

        Parameters:
            self (ban instance): ban to notif disabled decision
            request (django request): request to build email

        Returns:
            email: Notification email
        """
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
        """Method, return if the ban is active now or not.

        Parameters:
            self (ban): Ban to test if is active.

        Returns:
           is_active (boolean): Return True if the ban is active.

        """
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
    """Django signal, post save operations on Ban objects.
    Sync user's access state in ldap, call email notification if needed.

    """
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
    """Django signal, post delete operations on Ban objects.
    Sync user's access state in ldap.

    """
    user = kwargs["instance"].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    regen("mailing")
    regen("dhcp")
    regen("mac_ip_list")


class Whitelist(RevMixin, AclMixin, models.Model):
    """ A class representing a whitelist, which gives a free internet
    access to a user for special reason.
    Is overrided by a ban object.

    Attributes:
        user: related user for this whitelist
        raison: reason of this whitelist, can be null
        date_start: Date of the start of the whitelist
        date_end: Date of the end of the whitelist
    """

    user = models.ForeignKey("User", on_delete=models.PROTECT)
    raison = models.CharField(max_length=255)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField()

    class Meta:
        permissions = (("view_whitelist", _("Can view a whitelist object")),)
        verbose_name = _("whitelist (free of charge access)")
        verbose_name_plural = _("whitelists (free of charge access)")

    def is_active(self):
        """Method, returns if the whitelist is active now or not.

        Parameters:
            self (whitelist): Whitelist to test if is active.

        Returns:
           is_active (boolean): Return True if the whistelist is active.

        """
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
    """Django signal, post save operations on Whitelist objects.
    Sync user's access state in ldap.

    """
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
    """Django signal, post delete operations on Whitelist objects.
    Sync user's access state in ldap.

    """
    user = kwargs["instance"].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    regen("mailing")
    regen("dhcp")
    regen("mac_ip_list")


class Request(models.Model):
    """ A class representing for user's request of reset password by email, or
    confirm a new email address, with a link.

    Attributes:
        type: type of request (password, or confirm email address)
        token: single-user token for this request
        user: related user for this request
        email: If needed, related email to send the request and the link
        created_at: Date at the request was created
        expires_at: The request will be invalid after the expires_at date
    """

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


class EMailAddress(RevMixin, AclMixin, models.Model):
    """ A class representing an EMailAddress, for local emailaccounts
    support. Each emailaddress belongs to a user.

    Attributes:
        user: parent user address for this email
        local_part: local extension of the email
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
        """Shortcuts, returns a complete mailaddress from localpart and emaildomain
        specified in preferences.

        Parameters:
            self (emailaddress): emailaddress.

        Returns:
            emailaddress (string): Complete valid emailaddress

        """
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
        """Method, general clean for EMailAddres model.
        Clean email local_part field, checking if it is available by calling
        the smtp..

        Parameters:
            self (emailaddress): emailaddress local_part to clean.

        Returns:
            Django ValidationError, if the localpart does not comply with the policy.

        """
        self.local_part = self.local_part.lower()
        if "@" in self.local_part or "+" in self.local_part:
            raise ValidationError(_("The local part must not contain @ or +."))
        result, reason = smtp_check(self.local_part)
        if result:
            raise ValidationError(reason)
        super(EMailAddress, self).clean(*args, **kwargs)


class LdapUser(ldapdb.models.Model):
    """A class representing a LdapUser in LDAP, its LDAP conterpart.
    Synced from re2o django User model, (User django models),
    with a copy of its attributes/fields into LDAP, so this class is a mirror
    of the classic django User model.

    The basedn userdn is specified in settings.

    Attributes:
        name: The name of this User
        uid: The uid (login) for the unix user
        uidNumber: Linux uid number
        gid: The default gid number for this user
        sn: The user "str" pseudo
        login_shell: Linux shell for the user
        mail: Email address contact for this user
        display_name: Pretty display name for this user
        dialupAccess: Boolean, True for valid membership
        sambaSID: Identical id as uidNumber
        user_password: SSHA hashed password of user
        samba_nt_password: NTLM hashed password of user
        macs: Multivalued mac address
        shadowexpire: Set it to 0 to block access for this user and disabled
        account
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
    """A class representing a LdapUserGroup in LDAP, its LDAP conterpart.
    Synced from UserGroup, (ListRight/Group django models),
    with a copy of its attributes/fields into LDAP, so this class is a mirror
    of the classic django ListRight model.

    The basedn usergroupdn is specified in settings.

    Attributes:
        name: The name of this LdapUserGroup
        gid: The gid number for this unix group
        members: Users dn members of this LdapUserGroup
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
    """A class representing a ServiceUser in LDAP, its LDAP conterpart.
    Synced from ServiceUser, with a copy of its attributes/fields into LDAP,
    so this class is a mirror of the classic django ServiceUser model.

    The basedn userservicedn is specified in settings.

    Attributes:
        name: The name of this ServiceUser
        user_password: The SSHA hashed password of this ServiceUser
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
    """A class representing a ServiceUserGroup in LDAP, its LDAP conterpart.
    Synced from ServiceUserGroup, with a copy of its attributes/fields into LDAP,
    so this class is a mirror of the classic django ServiceUserGroup model.

    The basedn userservicegroupdn is specified in settings.

    Attributes:
        name: The name of this ServiceUserGroup
        members: ServiceUsers dn members of this ServiceUserGroup
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


