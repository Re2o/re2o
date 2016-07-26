from django.db import models
from django.db.models import Q
from django.forms import ModelForm, Form
from django import forms
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

import ldapdb.models
import ldapdb.models.fields

from re2o.settings import RIGHTS_LINK, REQ_EXPIRE_HRS, LDAP_SETTINGS
import re, uuid
import datetime

from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from topologie.models import Room
from cotisations.models import Cotisation, Facture, Vente
from machines.models import Interface, Machine

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
    UNIX_LOGIN_PATTERN = re.compile("^[a-z_][a-z0-9_-]*[$]?$")
    return UNIX_LOGIN_PATTERN.match(login)


def linux_user_validator(login):
    if not linux_user_check(login):
        raise forms.ValidationError(
                ", ce pseudo ('%(label)s') contient des carractères interdits",
                params={'label': login},
        )


def get_admin_right():
    try:
        admin_right = ListRight.objects.get(listright="admin")
    except ListRight.DoesNotExist:
        admin_right = ListRight(listright="admin")
        admin_right.save()
    return admin_right


class UserManager(BaseUserManager):
    def _create_user(self, pseudo, name, surname, email, password=None, su=False):
        if not pseudo:
            raise ValueError('Users must have an username')

        if not linux_user_check(pseudo):
            raise ValueError('Username shall only contain [a-z0-9_-]')

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
    STATE_ACTIVE = 0
    STATE_DEACTIVATED = 1
    STATE_ARCHIVED = 2
    STATES = (
            (0, 'STATE_ACTIVE'),
            (1, 'STATE_DEACTIVATED'),
            (2, 'STATE_ARCHIVED'),
            )

    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    pseudo = models.CharField(max_length=32, unique=True, help_text="Doit contenir uniquement des lettres, chiffres, ou tirets", validators=[linux_user_validator])
    email = models.EmailField()
    school = models.ForeignKey('School', on_delete=models.PROTECT, null=False, blank=False)
    shell = models.ForeignKey('ListShell', on_delete=models.PROTECT, null=False, blank=False, default=1)
    comment = models.CharField(help_text="Commentaire, promo", max_length=255, blank=True)
    room = models.OneToOneField('topologie.Room', on_delete=models.PROTECT, blank=True, null=True)
    pwd_ntlm = models.CharField(max_length=255)
    state = models.IntegerField(choices=STATES, default=STATE_ACTIVE)
    registered = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'pseudo'
    REQUIRED_FIELDS = ['name', 'surname', 'email']

    objects = UserManager()

    @property
    def is_active(self):
        return self.state == self.STATE_ACTIVE

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_admin(self):
        try:
            Right.objects.get(user=self, right__listright='admin')
        except Right.DoesNotExist:
            return False
        return True

    @is_admin.setter
    def is_admin(self, value):
        if value and not self.is_admin:
            self.make_admin()
        elif not value and self.is_admin:
            self.un_admin()

    def get_full_name(self):
        return '%s %s' % (self.name, self.surname)

    def get_short_name(self):
        return self.name

    def has_perms(self, perms, obj=None):
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

    def end_adhesion(self):
        date_max = Cotisation.objects.all().filter(vente=Vente.objects.all().filter(facture=Facture.objects.all().filter(user=self).exclude(valid=False))).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    def is_adherent(self):
        end = self.end_adhesion()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    def end_ban(self):
        """ Renvoie la date de fin de ban d'un user, False sinon """
        date_max = Ban.objects.all().filter(user=self).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    def end_whitelist(self):
        """ Renvoie la date de fin de ban d'un user, False sinon """
        date_max = Whitelist.objects.all().filter(user=self).aggregate(models.Max('date_end'))['date_end__max']
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
        return self.state == User.STATE_ACTIVE \
            and not self.is_ban() and (self.is_adherent() or self.is_whitelisted())

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
        try:
            user_ldap = LdapUser.objects.get(name=self.pseudo)
        except LdapUser.DoesNotExist:
            user_ldap = LdapUser(name=self.pseudo)
        if base:
            user_ldap.sn = self.pseudo
            user_ldap.dialupAccess = str(self.has_access())
            user_ldap.uidNumber = self.id
            user_ldap.home_directory = '/home/' + self.pseudo
            user_ldap.mail = self.email
            user_ldap.given_name = str(self.surname).lower() + '_' + str(self.name).lower()[:3]
            user_ldap.gid = LDAP_SETTINGS['user_gid']
            user_ldap.user_password = self.password
            user_ldap.sambat_nt_password = self.pwd_ntlm
        if access_refresh:
            user_ldap.dialupAccess = str(self.has_access())
        if mac_refresh:
            user_ldap.macs = [inter.mac_address for inter in Interface.objects.filter(machine=Machine.objects.filter(user=self))]
        user_ldap.save()

    def ldap_del(self):
        try:
            user_ldap = LdapUser.objects.get(name=self.pseudo)
            user_ldap.delete()
        except LdapUser.DoesNotExist:
            pass

    def __str__(self):
        return self.pseudo

@receiver(post_save, sender=User)
def user_post_save(sender, **kwargs):
    user = kwargs['instance']
    user.ldap_sync(base=True, access_refresh=True, mac_refresh=False)

@receiver(post_delete, sender=User)
def user_post_delete(sender, **kwargs):
    user = kwargs['instance']
    user.ldap_del()

class Right(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    right = models.ForeignKey('ListRight', on_delete=models.PROTECT)

    class Meta:
        unique_together = ("user", "right")

    def __str__(self):
        return str(self.user) + " - " + str(self.right)

@receiver(post_save, sender=Right)
def right_post_save(sender, **kwargs):
    right = kwargs['instance'].right
    right.ldap_sync()

@receiver(post_delete, sender=Right)
def right_post_delete(sender, **kwargs):
    right = kwargs['instance'].right
    right.ldap_sync()

class School(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ListRight(models.Model):
    listright = models.CharField(max_length=255, unique=True)
    gid = models.IntegerField(unique=True, null=True)

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
    right = kwargs['instance']
    right.ldap_sync()

@receiver(post_delete, sender=ListRight)
def listright_post_delete(sender, **kwargs):
    right = kwargs['instance']
    right.ldap_del()

class ListShell(models.Model):
    shell = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.shell

class Ban(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    raison = models.CharField(max_length=255)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField(help_text='%d/%m/%y %H:%M:%S')

    def __str__(self):
        return str(self.user) + ' ' + str(self.raison)


class Whitelist(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    raison = models.CharField(max_length=255)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField(help_text='%d/%m/%y %H:%M:%S')

    def __str__(self):
        return str(self.user) + ' ' + str(self.raison)

class Request(models.Model):
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
            self.expires_at = timezone.now() \
                + datetime.timedelta(hours=REQ_EXPIRE_HRS)
        if not self.token:
            self.token = str(uuid.uuid4()).replace('-', '')  # remove hyphens
        super(Request, self).save()

class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = LDAP_SETTINGS['base_user_dn']
    object_classes = ['inetOrgPerson','top','posixAccount','sambaSamAccount','radiusprofile']

    # attributes
    gid = ldapdb.models.fields.IntegerField(db_column='gidNumber')
    name = ldapdb.models.fields.CharField(db_column='cn', max_length=200, primary_key=True)
    uid = ldapdb.models.fields.CharField(db_column='uid', max_length=200)
    uidNumber = ldapdb.models.fields.IntegerField(db_column='uidNumber', unique=True)
    sn = ldapdb.models.fields.CharField(db_column='sn', max_length=200)
    loginShell = ldapdb.models.fields.CharField(db_column='loginShell', max_length=200, default="/bin/zsh")
    mail = ldapdb.models.fields.CharField(db_column='mail', max_length=200) 
    given_name = ldapdb.models.fields.CharField(db_column='givenName', max_length=200)
    home_directory = ldapdb.models.fields.CharField(db_column='homeDirectory', max_length=200)
    display_name = ldapdb.models.fields.CharField(db_column='displayName', max_length=200)
    dialupAccess = ldapdb.models.fields.CharField(db_column='dialupAccess')
    sambaSID = ldapdb.models.fields.IntegerField(db_column='sambaSID', unique=True)
    user_password = ldapdb.models.fields.CharField(db_column='userPassword', max_length=200, blank=True, null=True)
    sambat_nt_password = ldapdb.models.fields.CharField(db_column='sambaNTPassword', max_length=200, blank=True, null=True)
    macs = ldapdb.models.fields.ListField(db_column='radiusCallingStationId', max_length=200, blank=True, null=True)

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
    base_dn = LDAP_SETTINGS['base_usergroup_dn']
    object_classes = ['posixGroup']

    # attributes
    gid = ldapdb.models.fields.IntegerField(db_column='gidNumber')
    members = ldapdb.models.fields.ListField(db_column='memberUid', blank=True)
    name = ldapdb.models.fields.CharField(db_column='cn', max_length=200, primary_key=True)

    def __str__(self):
        return self.name

class BaseInfoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseInfoForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Nom'
        self.fields['surname'].label = 'Prénom'
        self.fields['school'].label = 'Établissement'
        self.fields['comment'].label = 'Commentaire'
        self.fields['room'].label = 'Chambre'
        self.fields['room'].empty_label = "Pas de chambre"
        self.fields['school'].empty_label = "Séléctionner un établissement"

    class Meta:
        model = User
        fields = [
            'name',
            'surname',
            'pseudo',
            'email',
            'school',
            'comment',
            'room',
        ]

class InfoForm(BaseInfoForm):
    force = forms.BooleanField(label="Forcer le déménagement ?", initial=False, required=False)

    def clean_force(self):
        if self.cleaned_data.get('force', False):
            remove_user_room(self.cleaned_data.get('room'))
        return

class UserForm(InfoForm):
    class Meta(InfoForm.Meta):
        fields = '__all__'

class PasswordForm(ModelForm):
    class Meta:
        model = User
        fields = ['password', 'pwd_ntlm']


class StateForm(ModelForm):
    class Meta:
        model = User
        fields = ['state']


class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(SchoolForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Établissement'

class ListRightForm(ModelForm):
    class Meta:
        model = ListRight
        fields = ['listright']

    def __init__(self, *args, **kwargs):
        super(ListRightForm, self).__init__(*args, **kwargs)
        self.fields['listright'].label = 'Nom du droit/groupe'

class NewListRightForm(ListRightForm):
    class Meta(ListRightForm.Meta):
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(NewListRightForm, self).__init__(*args, **kwargs)
        self.fields['gid'].label = 'Gid, attention, cet attribut ne doit pas être modifié après création'

class DelListRightForm(ModelForm):
    listrights = forms.ModelMultipleChoiceField(queryset=ListRight.objects.all(), label="Droits actuels",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['listright','gid']
        model = ListRight

class DelSchoolForm(ModelForm):
    schools = forms.ModelMultipleChoiceField(queryset=School.objects.all(), label="Etablissements actuels",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['name']
        model = School


class RightForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RightForm, self).__init__(*args, **kwargs)
        self.fields['right'].label = 'Droit'
        self.fields['right'].empty_label = "Choisir un nouveau droit"

    class Meta:
        model = Right
        fields = ['right']


class DelRightForm(ModelForm):
    rights = forms.ModelMultipleChoiceField(queryset=Right.objects.all(), label="Droits actuels",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Right
        exclude = ['user', 'right']


class BanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BanForm, self).__init__(*args, **kwargs)
        self.fields['date_end'].label = 'Date de fin'

    class Meta:
        model = Ban
        exclude = ['user']

    def clean_date_end(self):
        date_end = self.cleaned_data['date_end']
        if date_end < timezone.now():
            raise forms.ValidationError("Triple buse, la date de fin ne peut pas être avant maintenant... Re2o ne voyage pas dans le temps")
        return date_end


class WhitelistForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(WhitelistForm, self).__init__(*args, **kwargs)
        self.fields['date_end'].label = 'Date de fin'

    class Meta:
        model = Whitelist
        exclude = ['user']

    def clean_date_end(self):
        date_end = self.cleaned_data['date_end']
        if date_end < timezone.now():
            raise forms.ValidationError("Triple buse, la date de fin ne peut pas être avant maintenant... Re2o ne voyage pas dans le temps")
        return date_end


class ProfilForm(Form):
    user = forms.CharField(label='Ok', max_length=100)
