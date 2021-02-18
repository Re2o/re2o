import sys

import ldapdb.models
import ldapdb.models.fields
from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.dispatch import receiver

import machines.models
import users.models
import users.signals


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
    base_dn = settings.LDAP["base_user_dn"]
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


@receiver(users.signals.synchronise, sender=users.models.User)
def synchronise_user(sender, **kwargs):
    """
    Synchronise an User to the LDAP.
    Args:
        * sender : The model class.
        * instance : The actual instance being synchronised.
        * base : Default `True`. When `True`, synchronise basic attributes.
        * access_refresh : Default `True`. When `True`, synchronise the access time.
        * mac_refresh : Default `True`. When True, synchronise the list of mac addresses.
        * group_refresh: Default `False`. When `True` synchronise the groups of the instance.
    """
    base = kwargs.get("base", True)
    access_refresh = kwargs.get("access_refresh", True)
    mac_refresh = kwargs.get("mac_refresh", True)
    group_refresh = kwargs.get("group_refresh", False)

    user = kwargs["instance"]

    if sys.version_info[0] >= 3 and (
        user.state == user.STATE_ACTIVE
        or user.state == user.STATE_ARCHIVE
        or user.state == user.STATE_DISABLED
    ):
        user.refresh_from_db()
        try:
            user_ldap = LdapUser.objects.get(uidNumber=user.uid_number)
        except LdapUser.DoesNotExist:
            user_ldap = LdapUser(uidNumber=user.uid_number)
            base = True
            access_refresh = True
            mac_refresh = True
        if base:
            user_ldap.name = user.pseudo
            user_ldap.sn = user.pseudo
            user_ldap.dialupAccess = str(user.has_access())
            user_ldap.home_directory = user.home_directory
            user_ldap.mail = user.get_mail
            user_ldap.given_name = user.surname.lower() + "_" + user.name.lower()[:3]
            user_ldap.gid = settings.DEFAULT_GID
            if "{SSHA}" in user.password or "{SMD5}" in user.password:
                # We remove the extra $ added at import from ldap
                user_ldap.user_password = user.password[:6] + user.password[7:]
            elif "{crypt}" in user.password:
                # depending on the length, we need to remove or not a $
                if len(user.password) == 41:
                    user_ldap.user_password = user.password
                else:
                    user_ldap.user_password = user.password[:7] + user.password[8:]

            user_ldap.sambat_nt_password = user.pwd_ntlm.upper()
            if user.get_shell:
                user_ldap.login_shell = str(user.get_shell)
            user_ldap.shadowexpire = user.get_shadow_expire
        if access_refresh:
            user_ldap.dialupAccess = str(user.has_access())
        if mac_refresh:
            user_ldap.macs = [
                str(mac)
                for mac in machines.models.Interface.objects.filter(machine__user=user)
                .values_list("mac_address", flat=True)
                .distinct()
            ]
        if group_refresh:
            # Need to refresh all groups because we don't know which groups
            # were updated during edition of groups and the user may no longer
            # be part of the updated group (case of group removal)
            for group in Group.objects.all():
                if hasattr(group, "listright"):
                    synchronise_usergroup(
                        users.models.ListRight, instance=group.listright
                    )
        user_ldap.save()


@receiver(users.signals.remove, sender=users.models.User)
def remove_user(sender, **kwargs):
    user = kwargs["instance"]
    try:
        user_ldap = LdapUser.objects.get(name=user.pseudo)
        user_ldap.delete()
    except LdapUser.DoesNotExist:
        pass


@receiver(users.signals.remove_mass, sender=users.models.User)
def remove_users(sender, **kwargs):
    queryset_users = kwargs["queryset"]
    LdapUser.objects.filter(
        name__in=list(queryset_users.values_list("pseudo", flat=True))
    ).delete()


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
    base_dn = settings.LDAP["base_usergroup_dn"]
    object_classes = ["posixGroup"]

    # attributes
    gid = ldapdb.models.fields.IntegerField(db_column="gidNumber")
    members = ldapdb.models.fields.ListField(db_column="memberUid", blank=True)
    name = ldapdb.models.fields.CharField(
        db_column="cn", max_length=200, primary_key=True
    )

    def __str__(self):
        return self.name


@receiver(users.signals.synchronise, sender=users.models.ListRight)
def synchronise_usergroup(sender, **kwargs):
    group = kwargs["instance"]
    try:
        group_ldap = LdapUserGroup.objects.get(gid=group.gid)
    except LdapUserGroup.DoesNotExist:
        group_ldap = LdapUserGroup(gid=group.gid)
    group_ldap.name = group.unix_name
    group_ldap.members = [user.pseudo for user in group.user_set.all()]
    group_ldap.save()


@receiver(users.signals.remove, sender=users.models.ListRight)
def remove_usergroup(sender, **kwargs):
    group = kwargs["instance"]
    try:
        group_ldap = LdapUserGroup.objects.get(gid=group.gid)
        group_ldap.delete()
    except LdapUserGroup.DoesNotExist:
        pass


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
    base_dn = settings.LDAP["base_userservice_dn"]
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


def synchronise_serviceuser_group(serviceuser):
    try:
        group = LdapServiceUserGroup.objects.get(name=serviceuser.access_group)
    except:
        group = LdapServiceUserGroup(name=serviceuser.access_group)
    group.members = list(
        LdapServiceUser.objects.filter(
            name__in=[
                user.pseudo
                for user in users.models.ServiceUser.objects.filter(
                    access_group=serviceuser.access_group
                )
            ]
        ).values_list("dn", flat=True)
    )
    group.save()


@receiver(users.signals.synchronise, sender=users.models.ServiceUser)
def synchronise_serviceuser(sender, **kwargs):
    user = kwargs["instance"]
    try:
        user_ldap = LdapServiceUser.objects.get(name=user.pseudo)
    except LdapServiceUser.DoesNotExist:
        user_ldap = LdapServiceUser(name=user.pseudo)
    user_ldap.user_password = user.password[:6] + user.password[7:]
    user_ldap.save()
    synchronise_serviceuser_group(user)


@receiver(users.signals.remove, sender=users.models.ServiceUser)
def remove_serviceuser(sender, **kwargs):
    user = kwargs["instance"]
    try:
        user_ldap = LdapServiceUser.objects.get(name=user.pseudo)
        user_ldap.delete()
    except LdapUser.DoesNotExist:
        pass
    synchronise_serviceuser_group(user)


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
    base_dn = settings.LDAP["base_userservicegroup_dn"]
    object_classes = ["groupOfNames"]

    # attributes
    name = ldapdb.models.fields.CharField(
        db_column="cn", max_length=200, primary_key=True
    )
    members = ldapdb.models.fields.ListField(db_column="member", blank=True)

    def __str__(self):
        return self.name
