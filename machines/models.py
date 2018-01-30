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

from datetime import timedelta
import re
from netaddr import mac_bare, EUI, IPSet, IPRange, IPNetwork, IPAddress

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms import ValidationError
from django.utils.functional import cached_property
from django.utils import timezone
from django.core.validators import MaxValueValidator

from macaddress.fields import MACAddressField

from re2o.field_permissions import FieldPermissionModelMixin

import users.models
import preferences.models


class Machine(FieldPermissionModelMixin, models.Model):
    """ Class définissant une machine, object parent user, objets fils
    interfaces"""
    PRETTY_NAME = "Machine"

    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    name = models.CharField(
        max_length=255,
        help_text="Optionnel",
        blank=True,
        null=True
    )
    active = models.BooleanField(default=True)

    class Meta:
        permissions = (
            ("view_machine", "Peut voir un objet machine quelquonque"),
            ("change_machine_user", "Peut changer le propriétaire d'une machine"),
        )

    def get_instance(machineid, *args, **kwargs):
        """Récupère une instance
        :param machineid: Instance id à trouver
        :return: Une instance machine évidemment"""
        return Machine.objects.get(pk=machineid)

    @staticmethod
    def can_change_user(user_request, *args, **kwargs):
        """Checks if an user is allowed to change the user who owns a
        Machine.

        Args:
            user_request: The user requesting to change owner.

        Returns:
            A tuple with a boolean stating if edition is allowed and an
            explanation message.
        """
        return user_request.has_perm('machines.change_machine_user'), "Vous ne pouvez pas modifier l'utilisateur de la machine."

    def can_create(user_request, userid, *args, **kwargs):
        """Vérifie qu'un user qui fait la requète peut bien créer la machine
        et n'a pas atteint son quota, et crée bien une machine à lui
        :param user_request: Utilisateur qui fait la requête
        :param userid: id de l'user dont on va créer une machine
        :return: soit True, soit False avec la raison de l'échec"""
        try:
            user = users.models.User.objects.get(pk=userid)
        except users.models.User.DoesNotExist:
            return False, u"Utilisateur inexistant"
        options, created = preferences.models.OptionalMachine.objects.get_or_create()
        max_lambdauser_interfaces = options.max_lambdauser_interfaces
        if not user_request.has_perm('machines.add_machine'):
            if user != user_request:
                return False, u"Vous ne pouvez pas ajouter une machine à un\
                        autre user que vous sans droit"
            if user.user_interfaces().count() >= max_lambdauser_interfaces:
                return False, u"Vous avez atteint le maximum d'interfaces\
                        autorisées que vous pouvez créer vous même (%s) "\
                        % max_lambdauser_interfaces
        return True, None

    def can_edit(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien éditer cette instance particulière (soit
        machine de soi, soit droit particulier
        :param self: instance machine à éditer
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison le cas échéant"""
        if self.user != user_request:
            if not user_request.has_perm('machines.change_interface') or not self.user.can_edit(self.user, user_request, *args, **kwargs)[0]:
                return False, u"Vous ne pouvez pas éditer une machine\
                        d'un autre user que vous sans droit"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien supprimer cette instance particulière (soit
        machine de soi, soit droit particulier
        :param self: instance machine à supprimer
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if self.user != user_request:
            if not user_request.has_perm('machines.change_interface') or not self.user.can_edit(self.user, user_request, *args, **kwargs)[0]:
                return False, u"Vous ne pouvez pas éditer une machine\
                        d'un autre user que vous sans droit"
        return True, None

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des machines,
        droit particulier correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_machine'):
            return False, u"Vous ne pouvez pas afficher l'ensemble des machines sans permission"
        return True, None

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière (soit
        machine de soi, soit droit particulier
        :param self: instance machine à éditer
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_machine') and self.user != user_request:
            return False, u"Vous n'avez pas droit de voir les machines autre\
                que les vôtres"
        return True, None

    def __init__(self, *args, **kwargs):
        super(Machine, self).__init__(*args, **kwargs)
        self.field_permissions = {
            'user' : self.can_change_user,
        }

    def __str__(self):
        return str(self.user) + ' - ' + str(self.id) + ' - ' + str(self.name)


class MachineType(models.Model):
    """ Type de machine, relié à un type d'ip, affecté aux interfaces"""
    PRETTY_NAME = "Type de machine"

    type = models.CharField(max_length=255)
    ip_type = models.ForeignKey(
        'IpType',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    class Meta:
        permissions = (
            ("view_machinetype", "Peut voir un objet machinetype"),
            ("use_all_machinetype", "Peut utiliser n'importe quel type de machine"),
        )

    def all_interfaces(self):
        """ Renvoie toutes les interfaces (cartes réseaux) de type
        machinetype"""
        return Interface.objects.filter(type=self)

    def get_instance(machinetypeid, *args, **kwargs):
        """Récupère une instance
        :param machinetypeid: Instance id à trouver
        :return: Une instance machinetype évidemment"""
        return MachineType.objects.get(pk=machinetypeid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un type de machine
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_machinetype'), u"Vous n'avez pas le droit\
            de créer un type de machine"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance type de machine
        :param self: Instance machinetype à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_machinetype'):
            return False, u"Vous n'avez pas le droit d'éditer des types de machine"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien supprimer cette instance particulière (soit
        machinetype de soi, soit droit particulier
        :param self: instance machinetype à supprimer
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.delete_machinetype'):
            return False, u"Vous n'avez pas le droit de supprimer des types de machines"
        return True, None

    def can_use_all(user_request, *args, **kwargs):
        """Check if an user can use every MachineType.

        Args:
            user_request: The user requesting edition.
        Returns:
            A tuple with a boolean stating if user can acces and an explanation
            message is acces is not allowed.
        """
        if not user_request.has_perm('machines.use_all_machinetype'):
            return False, u"Vous n'avez pas le droit d'utiliser tout types de machines"
        return True, None

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des machinetype,
        droit particulier correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_machinetype'), u"Vous n'avez pas le droit\
            de voir les types de machines"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance machinetype à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_machinetype'), u"Vous n'avez pas le droit\
            de voir les types de machines"

    def __str__(self):
        return self.type


class IpType(models.Model):
    """ Type d'ip, définissant un range d'ip, affecté aux machine types"""
    PRETTY_NAME = "Type d'ip"

    type = models.CharField(max_length=255)
    extension = models.ForeignKey('Extension', on_delete=models.PROTECT)
    need_infra = models.BooleanField(default=False)
    domaine_ip_start = models.GenericIPAddressField(protocol='IPv4')
    domaine_ip_stop = models.GenericIPAddressField(protocol='IPv4')
    prefix_v6 = models.GenericIPAddressField(
        protocol='IPv6',
        null=True,
        blank=True
    )
    vlan = models.ForeignKey(
        'Vlan',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    ouverture_ports = models.ForeignKey(
        'OuverturePortList',
        blank=True,
        null=True
    )

    class Meta:
        permissions = (
            ("view_iptype", "Peut voir un objet iptype"),
            ("use_all_iptype", "Peut utiliser tous les iptype"),
        )

    @cached_property
    def ip_range(self):
        """ Renvoie un objet IPRange à partir de l'objet IpType"""
        return IPRange(self.domaine_ip_start, end=self.domaine_ip_stop)

    @cached_property
    def ip_set(self):
        """ Renvoie une IPSet à partir de l'iptype"""
        return IPSet(self.ip_range)

    @cached_property
    def ip_set_as_str(self):
        """ Renvoie une liste des ip en string"""
        return [str(x) for x in self.ip_set]

    def ip_objects(self):
        """ Renvoie tous les objets ipv4 relié à ce type"""
        return IpList.objects.filter(ip_type=self)

    def free_ip(self):
        """ Renvoie toutes les ip libres associées au type donné (self)"""
        return IpList.objects.filter(
            interface__isnull=True
        ).filter(ip_type=self)

    def gen_ip_range(self):
        """ Cree les IpList associées au type self. Parcours pédestrement et
        crée les ip une par une. Si elles existent déjà, met à jour le type
        associé à l'ip"""
        # Creation du range d'ip dans les objets iplist
        networks = []
        for net in self.ip_range.cidrs():
            networks += net.iter_hosts()
        ip_obj = [IpList(ip_type=self, ipv4=str(ip)) for ip in networks]
        listes_ip = IpList.objects.filter(
            ipv4__in=[str(ip) for ip in networks]
        )
        # Si il n'y a pas d'ip, on les crée
        if not listes_ip:
            IpList.objects.bulk_create(ip_obj)
        # Sinon on update l'ip_type
        else:
            listes_ip.update(ip_type=self)
        return

    def del_ip_range(self):
        """ Methode dépréciée, IpList est en mode cascade et supprimé
        automatiquement"""
        if Interface.objects.filter(ipv4__in=self.ip_objects()):
            raise ValidationError("Une ou plusieurs ip du range sont\
            affectées, impossible de supprimer le range")
        for ip in self.ip_objects():
            ip.delete()

    def clean(self):
        """ Nettoyage. Vérifie :
        - Que ip_stop est après ip_start
        - Qu'on ne crée pas plus gros qu'un /16
        - Que le range crée ne recoupe pas un range existant
        - Formate l'ipv6 donnée en /64"""
        if IPAddress(self.domaine_ip_start) > IPAddress(self.domaine_ip_stop):
            raise ValidationError("Domaine end doit être après start...")
        # On ne crée pas plus grand qu'un /16
        if self.ip_range.size > 65536:
            raise ValidationError("Le range est trop gros, vous ne devez\
            pas créer plus grand qu'un /16")
        # On check que les / ne se recoupent pas
        for element in IpType.objects.all().exclude(pk=self.pk):
            if not self.ip_set.isdisjoint(element.ip_set):
                raise ValidationError("Le range indiqué n'est pas disjoint\
                des ranges existants")
        # On formate le prefix v6
        if self.prefix_v6:
            self.prefix_v6 = str(IPNetwork(self.prefix_v6 + '/64').network)
        return

    def save(self, *args, **kwargs):
        self.clean()
        super(IpType, self).save(*args, **kwargs)

    def get_instance(iptypeid, *args, **kwargs):
        """Récupère une instance
        :param iptypeid: Instance id à trouver
        :return: Une instance iptype évidemment"""
        return IpType.objects.get(pk=iptypeid)

    def can_use_all(user_request, *args, **kwargs):
        """Superdroit qui permet d'utiliser toutes les extensions sans restrictions
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.use_all_iptype'), None


    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un type d'ip
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_iptype'), u"Vous n'avez pas le droit\
            de créer un type d'ip"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance iptype
        :param self: Instance iptype à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_iptype'):
            return False, u"Vous n'avez pas le droit d'éditer des types d'ip"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour supprimer
        cette instance iptype
        :param self: Instance iptype à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.delete_iptype'), u"Vous n'avez pas le droit\
            de supprimer un type d'ip"

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des iptype,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_iptype'), u"Vous n'avez pas le droit\
            de voir les types d'ip"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance iptype à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_iptype'), u"Vous n'avez pas le droit\
            de voir les types d'ip"

    def __str__(self):
        return self.type


class Vlan(models.Model):
    """ Un vlan : vlan_id et nom
    On limite le vlan id entre 0 et 4096, comme défini par la norme"""
    PRETTY_NAME = "Vlans"

    vlan_id = models.PositiveIntegerField(validators=[MaxValueValidator(4095)])
    name = models.CharField(max_length=256)
    comment = models.CharField(max_length=256, blank=True)

    class Meta:
        permissions = (
            ("view_vlan", "Peut voir un objet vlan"),
        )

    def get_instance(vlanid, *args, **kwargs):
        """Récupère une instance
        :param vlanid: Instance id à trouver
        :return: Une instance vlan évidemment"""
        return Vlan.objects.get(pk=vlanid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un vlan
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_vlan'), u"Vous n'avez pas le droit\
            de créer un vlan"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance vlan
        :param self: Instance vlan à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_vlan'):
            return False, u"Vous n'avez pas le droit d'éditer des vlans"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour supprimer
        cette instance vlan
        :param self: Instance vlan à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.delete_vlan'), u"Vous n'avez pas le droit\
            de suprimer un vlan"

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des vlan,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_vlan'), u"Vous n'avez pas le droit\
            de voir les vlans"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance vlan à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_vlan'), u"Vous n'avez pas le droit\
            de voir les vlans"

    def __str__(self):
        return self.name


class Nas(models.Model):
    """ Les nas. Associé à un machine_type.
    Permet aussi de régler le port_access_mode (802.1X ou mac-address) pour
    le radius. Champ autocapture de la mac à true ou false"""
    PRETTY_NAME = "Correspondance entre les nas et les machines connectées"

    default_mode = '802.1X'
    AUTH = (
        ('802.1X', '802.1X'),
        ('Mac-address', 'Mac-address'),
    )

    name = models.CharField(max_length=255, unique=True)
    nas_type = models.ForeignKey(
        'MachineType',
        on_delete=models.PROTECT,
        related_name='nas_type'
    )
    machine_type = models.ForeignKey(
        'MachineType',
        on_delete=models.PROTECT,
        related_name='machinetype_on_nas'
    )
    port_access_mode = models.CharField(
        choices=AUTH,
        default=default_mode,
        max_length=32
    )
    autocapture_mac = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("view_nas", "Peut voir un objet Nas"),
        )

    def get_instance(nasid, *args, **kwargs):
        """Récupère une instance
        :param nasid: Instance id à trouver
        :return: Une instance nas évidemment"""
        return Nas.objects.get(pk=nasid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un nas
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_nas'), u"Vous n'avez pas le droit\
            de créer un nas"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance nas
        :param self: Instance nas à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_nas'):
            return False, u"Vous n'avez pas le droit d'éditer des nas"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour supprimer
        cette instance nas
        :param self: Instance nas à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.delete_nas'), u"Vous n'avez pas le droit\
            de supprimer un nas"

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des nas,
        droit particulier view objet correspondant

        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_nas'), u"Vous n'avez pas le droit\
            de voir les nas"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance nas à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_nas'), u"Vous n'avez pas le droit\
            de voir les nas"

    def __str__(self):
        return self.name


class SOA(models.Model):
    """
    Un enregistrement SOA associé à une extension
    Les valeurs par défault viennent des recommandations RIPE :
    https://www.ripe.net/publications/docs/ripe-203
    """
    PRETTY_NAME = "Enregistrement SOA"

    name = models.CharField(max_length=255)
    mail = models.EmailField(
        help_text='Email du contact pour la zone'
    )
    refresh = models.PositiveIntegerField(
        default=86400,    # 24 hours
        help_text='Secondes avant que les DNS secondaires doivent demander le\
                   serial du DNS primaire pour détecter une modification'
    )
    retry = models.PositiveIntegerField(
        default=7200,    # 2 hours
        help_text='Secondes avant que les DNS secondaires fassent une nouvelle\
                   demande de serial en cas de timeout du DNS primaire'
    )
    expire = models.PositiveIntegerField(
        default=3600000, # 1000 hours
        help_text='Secondes après lesquelles les DNS secondaires arrêtent de\
                   de répondre aux requêtes en cas de timeout du DNS primaire'
    )
    ttl = models.PositiveIntegerField(
        default=172800,  # 2 days
        help_text='Time To Live'
    )

    class Meta:
        permissions = (
            ("view_soa", "Peut voir un objet soa"),
        )

    def get_instance(soaid, *args, **kwargs):
        """Récupère une instance
        :param soaid: Instance id à trouver
        :return: Une instance soa évidemment"""
        return SOA.objects.get(pk=soaid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un soa
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_soa'), u"Vous n'avez pas le droit\
            de créer un enregistrement SOA"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance soa
        :param self: Instance soa à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_soa'):
            return False, u"Vous n'avez pas le droit d'éditer des enregistrements SOA"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour supprimer
        cette instance soa
        :param self: Instance soa à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.delete_soa'), u"Vous n'avez pas le droit\
            de supprimer des enregistrements SOA"

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des soa,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_soa'), u"Vous n'avez pas le droit\
            de voir les enreistrement SOA"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance soa à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_soa'), u"Vous n'avez pas le droit\
            de voir les enreistrement SOA"

    def __str__(self):
        return str(self.name)

    @cached_property
    def dns_soa_param(self):
        """
        Renvoie la partie de l'enregistrement SOA correspondant aux champs :
            <refresh>   ; refresh
            <retry>     ; retry
            <expire>    ; expire
            <ttl>       ; TTL
        """
        return (
            '    {refresh}; refresh\n'
            '    {retry}; retry\n'
            '    {expire}; expire\n'
            '    {ttl}; TTL'
        ).format(
            refresh=str(self.refresh).ljust(12),
            retry=str(self.retry).ljust(12),
            expire=str(self.expire).ljust(12),
            ttl=str(self.ttl).ljust(12)
        )

    @cached_property
    def dns_soa_mail(self):
        """ Renvoie le mail dans l'enregistrement SOA """
        mail_fields = str(self.mail).split('@')
        return mail_fields[0].replace('.', '\\.') + '.' + mail_fields[1] + '.'

    @classmethod
    def new_default_soa(cls):
        """ Fonction pour créer un SOA par défaut, utile pour les nouvelles
        extensions .
        /!\ Ne jamais supprimer ou renommer cette fonction car elle est
        utilisée dans les migrations de la BDD. """
        return cls.objects.get_or_create(name="SOA to edit", mail="postmaser@example.com")[0].pk



class Extension(models.Model):
    """ Extension dns type example.org. Précise si tout le monde peut
    l'utiliser, associé à un origin (ip d'origine)"""
    PRETTY_NAME = "Extensions dns"

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Nom de la zone, doit commencer par un point (.example.org)"
    )
    need_infra = models.BooleanField(default=False)
    origin = models.OneToOneField(
        'IpList',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="Enregistrement A associé à la zone"
    )
    origin_v6 = models.GenericIPAddressField(
        protocol='IPv6',
        null=True,
        blank=True,
        help_text="Enregistrement AAAA associé à la zone"
    )
    soa = models.ForeignKey(
        'SOA',
        on_delete=models.CASCADE,
        default=SOA.new_default_soa
    )

    class Meta:
        permissions = (
            ("view_extension", "Peut voir un objet extension"),
            ("use_all_extension", "Peut utiliser toutes les extension"),
        )

    @cached_property
    def dns_entry(self):
        """ Une entrée DNS A et AAAA sur origin (zone self)"""
        entry = ""
        if self.origin:
            entry += "@               IN  A       " + str(self.origin)
        if self.origin_v6:
            if entry:
                entry += "\n"
            entry += "@               IN  AAAA    " + str(self.origin_v6)
        return entry

    def get_instance(extensionid, *args, **kwargs):
        """Récupère une instance
        :param extensionid: Instance id à trouver
        :return: Une instance extension évidemment"""
        return Extension.objects.get(pk=extensionid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        une extension
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_extension'), u"Vous n'avez pas le droit\
            de créer une extension"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance extension
        :param self: Instance extension à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_extension'):
            return False, u"Vous n'avez pas le droit d'éditer des extensions"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour supprimer
        cette instance extension
        :param self: Instance extension à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.delete_extension'), u"Vous n'avez pas le droit\
            de supprimer des extension"

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des extension,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_extension'), u"Vous n'avez pas le droit\
            de voir les extensions"

    def can_use_all(user_request, *args, **kwargs):
        """Superdroit qui permet d'utiliser toutes les extensions sans restrictions
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.use_all_extension'), None

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance extension à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_extension'), u"Vous n'avez pas le droit\
            de voir les extensions"

    def __str__(self):
        return self.name

    def clean(self, *args, **kwargs):
        if self.name and self.name[0] != '.':
            raise ValidationError("Une extension doit commencer par un point")
        super(Extension, self).clean(*args, **kwargs)


class Mx(models.Model):
    """ Entrées des MX. Enregistre la zone (extension) associée et la
    priorité
    Todo : pouvoir associer un MX à une interface """
    PRETTY_NAME = "Enregistrements MX"

    zone = models.ForeignKey('Extension', on_delete=models.PROTECT)
    priority = models.PositiveIntegerField(unique=True)
    name = models.OneToOneField('Domain', on_delete=models.PROTECT)

    class Meta:
        permissions = (
            ("view_mx", "Peut voir un objet mx"),
        )

    @cached_property
    def dns_entry(self):
        """Renvoie l'entrée DNS complète pour un MX à mettre dans les
        fichiers de zones"""
        return "@               IN  MX  " + str(self.priority).ljust(3) + " " + str(self.name)

    def get_instance(mxid, *args, **kwargs):
        """Récupère une instance
        :param mxid: Instance id à trouver
        :return: Une instance mx évidemment"""
        return Mx.objects.get(pk=mxid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un mx
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_mx'), u"Vous n'avez pas le droit\
            de créer un enregistrement MX"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance mx
        :param self: Instance mx à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_mx'):
            return False, u"Vous n'avez pas le droit d'éditer des enregstrements MX"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour del
        cette instance mx
        :param self: Instance mx à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.delete_mx'), u"Vous n'avez pas le droit\
            de supprimer un enregistrement MX"

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des mx,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_mx'), u"Vous n'avez pas le droit\
            de voir les enregistrements MX"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance mx à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_mx'), u"Vous n'avez pas le droit\
            de voir les enregistrements MX"

    def __str__(self):
        return str(self.zone) + ' ' + str(self.priority) + ' ' + str(self.name)


class Ns(models.Model):
    """Liste des enregistrements name servers par zone considéérée"""
    PRETTY_NAME = "Enregistrements NS"

    zone = models.ForeignKey('Extension', on_delete=models.PROTECT)
    ns = models.OneToOneField('Domain', on_delete=models.PROTECT)

    class Meta:
        permissions = (
            ("view_ns", "Peut voir un objet ns"),
        )

    @cached_property
    def dns_entry(self):
        """Renvoie un enregistrement NS complet pour les filezones"""
        return "@               IN  NS      " + str(self.ns)

    def get_instance(nsid, *args, **kwargs):
        """Récupère une instance
        :param nsid: Instance id à trouver
        :return: Une instance ns évidemment"""
        return Ns.objects.get(pk=nsid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un ns
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_ns'), u"Vous n'avez pas le droit\
            de créer un enregistrement NS"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance ns
        :param self: Instance ns à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_ns'):
            return False, u"Vous n'avez pas le droit d'éditer des enregistrements NS"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour del
        cette instance ns
        :param self: Instance ns à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.del_ns'), u"Vous n'avez pas le droit\
            de supprimer un enregistrement NS"

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des ns,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_ns'), u"Vous n'avez pas le droit\
            de voir les enregistrements NS"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance ns à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_ns'), u"Vous n'avez pas le droit\
            de voir les enregistrements NS"

    def __str__(self):
        return str(self.zone) + ' ' + str(self.ns)


class Txt(models.Model):
    """ Un enregistrement TXT associé à une extension"""
    PRETTY_NAME = "Enregistrement TXT"

    zone = models.ForeignKey('Extension', on_delete=models.PROTECT)
    field1 = models.CharField(max_length=255)
    field2 = models.TextField(max_length=2047)

    class Meta:
        permissions = (
            ("view_txt", "Peut voir un objet txt"),
        )

    def get_instance(txtid, *args, **kwargs):
        """Récupère une instance
        :param txtid: Instance id à trouver
        :return: Une instance txt évidemment"""
        return Txt.objects.get(pk=txtid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un txt
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_txt'), u"Vous n'avez pas le droit\
            de créer un enregistrement TXT"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance txt
        :param self: Instance txt à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_txt'):
            return False, u"Vous n'avez pas le droit d'éditer des enregistrement TXT"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour del
        cette instance txt
        :param self: Instance txt à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.delete_txt'), u"Vous n'avez pas le droit\
            de supprimer des enregistrements TXT"

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des txt,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_txt'), u"Vous n'avez pas le droit\
            de voir les enregistrements TXT"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance txt à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_txt'), u"Vous n'avez pas le droit\
            de voir les enregistrements TXT"

    def __str__(self):
        return str(self.zone) + " : " + str(self.field1) + " " +\
            str(self.field2)

    @cached_property
    def dns_entry(self):
        """Renvoie l'enregistrement TXT complet pour le fichier de zone"""
        return str(self.field1).ljust(15) + " IN  TXT     " + str(self.field2)


class Srv(models.Model):
    PRETTY_NAME = "Enregistrement Srv"

    TCP = 'TCP'
    UDP = 'UDP'

    service =  models.CharField(max_length=31)
    protocole = models.CharField(
        max_length=3,
        choices=(
            (TCP, 'TCP'),
            (UDP, 'UDP'),
            ),
        default=TCP,
    )
    extension = models.ForeignKey('Extension', on_delete=models.PROTECT)
    ttl = models.PositiveIntegerField(
        default=172800,  # 2 days
        help_text='Time To Live'
    )
    priority = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(65535)],
        help_text="La priorité du serveur cible (valeur entière non négative,\
            plus elle est faible, plus ce serveur sera utilisé s'il est disponible)"

    )
    weight = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(65535)],
        help_text="Poids relatif pour les enregistrements de même priorité\
            (valeur entière de 0 à 65535)"
    )
    port = models.PositiveIntegerField(
        validators=[MaxValueValidator(65535)],
        help_text="Port (tcp/udp)"
    )
    target = models.ForeignKey(
        'Domain',
        on_delete=models.PROTECT,
        help_text="Serveur cible"
    )

    class Meta:
        permissions = (
            ("view_soa", "Peut voir un objet soa"),
        )

    def get_instance(srvid, *args, **kwargs):
        """Récupère une instance
        :param srvid: Instance id à trouver
        :return: Une instance srv évidemment"""
        return Srv.objects.get(pk=srvid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un srv
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_soa'), u"Vous n'avez pas le droit\
            de créer un enregistrement SRV"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance srv
        :param self: Instance srv à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_soa'):
            return False, u"Vous n'avez pas le droit d'éditer des enregistrements SRV"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour del
        cette instance srv
        :param self: Instance srv à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.delete_soa'), u"Vous n'avez pas le droit\
            de supprimer un enregistrement SRV"

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des srv,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_soa'), u"Vous n'avez pas le droit\
            de voir les enregistrements SRV"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance srv à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_soa'), u"Vous n'avez pas le droit\
            de voir les enregistrements SRV"

    def __str__(self):
        return str(self.service) + ' ' + str(self.protocole) + ' ' +\
            str(self.extension) + ' ' + str(self.priority) +\
            ' ' + str(self.weight) + str(self.port) + str(self.target)

    @cached_property
    def dns_entry(self):
        """Renvoie l'enregistrement SRV complet pour le fichier de zone"""
        return str(self.service) + '._' + str(self.protocole).lower() +\
            str(self.extension) + '. ' + str(self.ttl) + ' IN SRV ' +\
            str(self.priority) + ' ' + str(self.weight) + ' ' +\
            str(self.port) + ' ' + str(self.target) + '.'


class Interface(FieldPermissionModelMixin,models.Model):
    """ Une interface. Objet clef de l'application machine :
    - une address mac unique. Possibilité de la rendre unique avec le
    typemachine
    - une onetoone vers IpList pour attribution ipv4
    - le type parent associé au range ip et à l'extension
    - un objet domain associé contenant son nom
    - la liste des ports oiuvert"""
    PRETTY_NAME = "Interface"

    ipv4 = models.OneToOneField(
        'IpList',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    mac_address = MACAddressField(integer=False, unique=True)
    machine = models.ForeignKey('Machine', on_delete=models.CASCADE)
    type = models.ForeignKey('MachineType', on_delete=models.PROTECT)
    details = models.CharField(max_length=255, blank=True)
    port_lists = models.ManyToManyField('OuverturePortList', blank=True)

    class Meta:
        permissions = (
            ("view_interface", "Peut voir un objet interface"),
            ("change_interface_machine", "Peut changer le propriétaire d'une interface"),
        )

    @cached_property
    def is_active(self):
        """ Renvoie si une interface doit avoir accès ou non """
        machine = self.machine
        user = self.machine.user
        return machine.active and user.has_access()

    @cached_property
    def ipv6_slaac(self):
        """ Renvoie un objet type ipv6 à partir du prefix associé à
        l'iptype parent"""
        if self.type.ip_type.prefix_v6:
            return EUI(self.mac_address).ipv6(
                IPNetwork(self.type.ip_type.prefix_v6).network
            )
        else:
            return None

    def sync_ipv6_slaac(self):
        """Cree, mets à jour et supprime si il y a lieu l'ipv6 slaac associée
        à la machine
        Sans prefixe ipv6, on return
        Si l'ip slaac n'est pas celle qu'elle devrait être, on maj"""
        ipv6_slaac = self.ipv6_slaac
        if not ipv6_slaac:
            return
        ipv6_object = Ipv6List.objects.filter(interface=self, slaac_ip=True).first()
        if not ipv6_object:
            ipv6_object = Ipv6List(interface=self, slaac_ip=True)
        if ipv6_object.ipv6 != str(ipv6_slaac):
            ipv6_object.ipv6 = str(ipv6_slaac)
            ipv6_object.save()

    def ipv6(self):
        """ Renvoie le queryset de la liste des ipv6
        On renvoie l'ipv6 slaac que si le mode slaac est activé (et non dhcpv6)"""
        machine_options, _created = preferences.models.OptionalMachine.objects.get_or_create()
        if machine_options.ipv6_mode == 'SLAAC':
            return Ipv6List.objects.filter(interface=self)
        else:
            return Ipv6List.objects.filter(interface=self, slaac_ip=False)

    def mac_bare(self):
        """ Formatage de la mac type mac_bare"""
        return str(EUI(self.mac_address, dialect=mac_bare)).lower()

    def filter_macaddress(self):
        """ Tente un formatage mac_bare, si échoue, lève une erreur de
        validation"""
        try:
            self.mac_address = str(EUI(self.mac_address))
        except:
            raise ValidationError("La mac donnée est invalide")

    def clean(self, *args, **kwargs):
        """ Formate l'addresse mac en mac_bare (fonction filter_mac)
        et assigne une ipv4 dans le bon range si inexistante ou incohérente"""
        # If type was an invalid value, django won't create an attribute type
        # but try clean() as we may be able to create it from another value
        # so even if the error as yet been detected at this point, django
        # continues because the error might not prevent us from creating the
        # instance.
        # But in our case, it's impossible to create a type value so we raise
        # the error.
        if not hasattr(self, 'type') :
            raise ValidationError("Le type d'ip choisi n'est pas valide")
        self.filter_macaddress()
        self.mac_address = str(EUI(self.mac_address)) or None
        if not self.ipv4 or self.type.ip_type != self.ipv4.ip_type:
            self.assign_ipv4()
        super(Interface, self).clean(*args, **kwargs)

    def assign_ipv4(self):
        """ Assigne une ip à l'interface """
        free_ips = self.type.ip_type.free_ip()
        if free_ips:
            self.ipv4 = free_ips[0]
        else:
            raise ValidationError("Il n'y a plus d'ip disponibles\
            dans le slash")
        return

    def unassign_ipv4(self):
        """ Sans commentaire, désassigne une ipv4"""
        self.ipv4 = None

    def update_type(self):
        """ Lorsque le machinetype est changé de type d'ip, on réassigne"""
        self.clean()
        self.save()

    def save(self, *args, **kwargs):
        self.filter_macaddress()
        # On verifie la cohérence en forçant l'extension par la méthode
        if self.ipv4:
            if self.type.ip_type != self.ipv4.ip_type:
                raise ValidationError("L'ipv4 et le type de la machine ne\
                correspondent pas")
        super(Interface, self).save(*args, **kwargs)

    def get_instance(interfaceid, *args, **kwargs):
        """Récupère une instance
        :param interfaceid: Instance id à trouver
        :return: Une instance interface évidemment"""
        return Interface.objects.get(pk=interfaceid)

    def can_create(user_request, machineid, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        une interface, ou bien que la machine appartient bien à l'user
        :param macineid: Id de la machine parente de l'interface
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        try:
            machine = Machine.objects.get(pk=machineid)
        except Machine.DoesNotExist:
            return False, u"Machine inexistante"
        if not user_request.has_perm('machines.add_interface'):
            options, created = preferences.models.OptionalMachine.objects.get_or_create()
            max_lambdauser_interfaces = options.max_lambdauser_interfaces
            if machine.user != user_request:
                return False, u"Vous ne pouvez pas ajouter une interface à une\
                        machine d'un autre user que vous sans droit"
            if machine.user.user_interfaces().count() >= max_lambdauser_interfaces:
                return False, u"Vous avez atteint le maximum d'interfaces\
                        autorisées que vous pouvez créer vous même (%s) "\
                        % max_lambdauser_interfaces
        return True, None

    @staticmethod
    def can_change_machine(user_request, *args, **kwargs):
        return user_request.has_perm('machines.change_interface_machine'), "Droit requis pour changer la machine"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance interface, ou qu'elle lui appartient
        :param self: Instance interface à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if self.machine.user != user_request:
            if not user_request.has_perm('machines.change_interface') or not self.machine.user.can_edit(user_request, *args, **kwargs)[0]:
                return False, u"Vous ne pouvez pas éditer une machine\
                    d'un autre user que vous sans droit"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits delete object pour del
        cette instance interface, ou qu'elle lui appartient
        :param self: Instance interface à del
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if self.machine.user != user_request:
            if not user_request.has_perm('machines.change_interface') or not self.machine.user.can_edit(user_request, *args, **kwargs)[0]:
                return False, u"Vous ne pouvez pas éditer une machine\
                        d'un autre user que vous sans droit"
        return True, None

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des interfaces,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_interface'):
            return False, u"Vous n'avez pas le droit de voir des machines autre\
                que les vôtres"
        return True, None

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet ou qu'elle appartient à l'user
        :param self: instance interface à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_interface') and self.machine.user != user_request:
            return False, u"Vous n'avez pas le droit de voir des machines autre\
                que les vôtres"
        return True, None

    def __init__(self, *args, **kwargs):
        super(Interface, self).__init__(*args, **kwargs)
        self.field_permissions = {
            'machine' : self.can_change_machine,
        }

    def __str__(self):
        try:
            domain = self.domain
        except:
            domain = None
        return str(domain)

    def has_private_ip(self):
        """ True si l'ip associée est privée"""
        if self.ipv4:
            return IPAddress(str(self.ipv4)).is_private()
        else:
            return False

    def may_have_port_open(self):
        """ True si l'interface a une ip et une ip publique.
        Permet de ne pas exporter des ouvertures sur des ip privées
        (useless)"""
        return self.ipv4 and not self.has_private_ip()


class Ipv6List(FieldPermissionModelMixin, models.Model):
    PRETTY_NAME = 'Enregistrements Ipv6 des machines'

    ipv6 = models.GenericIPAddressField(
        protocol='IPv6',
        unique=True
    )
    interface = models.ForeignKey('Interface', on_delete=models.CASCADE)
    slaac_ip = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("view_ipv6list", "Peut voir un objet ipv6"),
            ("change_ipv6list_slaac_ip", "Peut changer la valeur slaac sur une ipv6"),
        )

    def get_instance(ipv6listid, *args, **kwargs):
        """Récupère une instance
        :param interfaceid: Instance id à trouver
        :return: Une instance interface évidemment"""
        return Ipv6List.objects.get(pk=ipv6listid)

    def can_create(user_request, interfaceid, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        une ipv6, ou possède l'interface associée
        :param interfaceid: Id de l'interface associée à cet objet domain
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        try:
            interface = Interface.objects.get(pk=interfaceid)
        except Interface.DoesNotExist:
            return False, u"Interface inexistante"
        if not user_request.has_perm('machines.add_ipv6list'):
            if interface.machine.user != user_request:
                return False, u"Vous ne pouvez pas ajouter un alias à une\
                        machine d'un autre user que vous sans droit"
        return True, None

    @staticmethod
    def can_change_slaac_ip(user_request, *args, **kwargs):
        return user_request.has_perm('machines.change_ipv6list_slaac_ip'), "Droit requis pour changer la valeur slaac ip"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance interface, ou qu'elle lui appartient
        :param self: Instance interface à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if self.interface.machine.user != user_request:
            if not user_request.has_perm('machines.change_ipv6list') or not self.interface.machine.user.can_edit(user_request, *args, **kwargs)[0]:
                return False, u"Vous ne pouvez pas éditer une machine\
                    d'un autre user que vous sans droit"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits delete object pour del
        cette instance interface, ou qu'elle lui appartient
        :param self: Instance interface à del
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if self.interface.machine.user != user_request:
            if not user_request.has_perm('machines.change_ipv6list') or not self.interface.machine.user.can_edit(user_request, *args, **kwargs)[0]:
                return False, u"Vous ne pouvez pas éditer une machine\
                        d'un autre user que vous sans droit"
        return True, None

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des interfaces,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_ipv6list'):
            return False, u"Vous n'avez pas le droit de voir des machines autre\
                que les vôtres"
        return True, None

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet ou qu'elle appartient à l'user
        :param self: instance interface à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_ipv6list') and self.interface.machine.user != user_request:
            return False, u"Vous n'avez pas le droit de voir des machines autre\
                que les vôtres"
        return True, None

    def __init__(self, *args, **kwargs):
        super(Ipv6List, self).__init__(*args, **kwargs)
        self.field_permissions = {
            'slaac_ip' : self.can_change_slaac_ip,
        }

    def clean(self, *args, **kwargs):
        if self.slaac_ip and Ipv6List.objects.filter(interface=self.interface, slaac_ip=True).exclude(id=self.id):
            raise ValidationError("Une ip slaac est déjà enregistrée")
        super(Ipv6List, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Force à avoir appellé clean avant"""
        self.full_clean()
        super(Ipv6List, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.ipv6)


class Domain(models.Model):
    """ Objet domain. Enregistrement A et CNAME en même temps : permet de
    stocker les alias et les nom de machines, suivant si interface_parent
    ou cname sont remplis"""
    PRETTY_NAME = "Domaine dns"

    interface_parent = models.OneToOneField(
        'Interface',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.CharField(
        help_text="Obligatoire et unique, ne doit pas comporter de points",
        max_length=255
    )
    extension = models.ForeignKey('Extension', on_delete=models.PROTECT)
    cname = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='related_domain'
    )

    class Meta:
        unique_together = (("name", "extension"),)
        permissions = (
            ("view_domain", "Peut voir un objet domain"),
        )

    def get_extension(self):
        """ Retourne l'extension de l'interface parente si c'est un A
         Retourne l'extension propre si c'est un cname, renvoie None sinon"""
        if self.interface_parent:
            return self.interface_parent.type.ip_type.extension
        elif hasattr(self, 'extension'):
            return self.extension
        else:
            return None

    def clean(self):
        """ Validation :
        - l'objet est bien soit A soit CNAME
        - le cname est pas pointé sur lui-même
        - le nom contient bien les caractères autorisés par la norme
        dns et moins de 63 caractères au total
        - le couple nom/extension est bien unique"""
        if self.get_extension():
            self.extension = self.get_extension()
        if self.interface_parent and self.cname:
            raise ValidationError("On ne peut créer à la fois A et CNAME")
        if self.cname == self:
            raise ValidationError("On ne peut créer un cname sur lui même")
        HOSTNAME_LABEL_PATTERN = re.compile(
            "(?!-)[A-Z\d-]+(?<!-)$",
            re.IGNORECASE
        )
        dns = self.name.lower()
        if len(dns) > 63:
            raise ValidationError("Le nom de domaine %s est trop long\
            (maximum de 63 caractères)." % dns)
        if not HOSTNAME_LABEL_PATTERN.match(dns):
            raise ValidationError("Ce nom de domaine %s contient des\
            carractères interdits." % dns)
        self.validate_unique()
        super(Domain, self).clean()

    @cached_property
    def dns_entry(self):
        """ Une entrée DNS"""
        if self.cname:
            return str(self.name).ljust(15) + " IN CNAME   " + str(self.cname) + "."

    def save(self, *args, **kwargs):
        """ Empèche le save sans extension valide.
        Force à avoir appellé clean avant"""
        if not self.get_extension():
            raise ValidationError("Extension invalide")
        self.full_clean()
        super(Domain, self).save(*args, **kwargs)

    @cached_property
    def get_source_interface(self):
        """Renvoie l'interface source :
        - l'interface reliée si c'est un A
        - si c'est un cname, suit le cname jusqu'à atteindre le A
        et renvoie l'interface parente
        Fonction récursive"""
        if self.interface_parent:
            return self.interface_parent
        else:
            return self.cname.get_parent_interface()

    def get_instance(domainid, *args, **kwargs):
        """Récupère une instance
        :param domainid: Instance id à trouver
        :return: Une instance domain évidemment"""
        return Domain.objects.get(pk=domainid)

    def can_create(user_request, interfaceid, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un domain, ou possède l'interface associée
        :param interfaceid: Id de l'interface associée à cet objet domain
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        try:
            interface = Interface.objects.get(pk=interfaceid)
        except Interface.DoesNotExist:
            return False, u"Interface inexistante"
        if not user_request.has_perm('machines.add_domain'):
            options, created = preferences.models.OptionalMachine.objects.get_or_create()
            max_lambdauser_aliases = options.max_lambdauser_aliases
            if interface.machine.user != user_request:
                return False, u"Vous ne pouvez pas ajouter un alias à une\
                        machine d'un autre user que vous sans droit"
            if Domain.objects.filter(
                    cname__in=Domain.objects.filter(
                        interface_parent__in=interface.machine.user.user_interfaces()
                    )
                ).count() >= max_lambdauser_aliases:
                return False, u"Vous avez atteint le maximum d'alias\
                        autorisés que vous pouvez créer vous même (%s) "\
                        % max_lambdauser_aliases
        return True, None

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits pour editer
        cette instance domain
        :param self: Instance domain à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_domain') and\
            self.get_source_interface.machine.user != user_request:
            return False, u"Vous ne pouvez pas editer un alias à une machine\
                    d'un autre user que vous sans droit"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits delete object pour del
        cette instance domain, ou qu'elle lui appartient
        :param self: Instance domain à del
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.delete_domain') and\
            self.get_source_interface.machine.user != user_request:
            return False, u"Vous ne pouvez pas supprimer un alias à une machine\
                d'un autre user que vous sans droit"
        return True, None

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des domain,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_domain'):
            return False, u"Vous ne pouvez pas supprimer un alias à une machine\
                d'un autre user que vous sans droit"
        return True, None

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet ou qu'elle appartient à l'user
        :param self: instance domain à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_domain') and\
            self.get_source_interface.machine.user != user_request:
            return False, u"Vous n'avez pas le droit de voir des machines autre\
                que les vôtres"
        return True, None

    def __str__(self):
        return str(self.name) + str(self.extension)


class IpList(models.Model):
    PRETTY_NAME = "Addresses ipv4"

    ipv4 = models.GenericIPAddressField(protocol='IPv4', unique=True)
    ip_type = models.ForeignKey('IpType', on_delete=models.CASCADE)

    class Meta:
        permissions = (
            ("view_iplist", "Peut voir un objet iplist"),
        )

    @cached_property
    def need_infra(self):
        """ Permet de savoir si un user basique peut assigner cette ip ou
        non"""
        return self.ip_type.need_infra

    def clean(self):
        """ Erreur si l'ip_type est incorrect"""
        if not str(self.ipv4) in self.ip_type.ip_set_as_str:
            raise ValidationError("L'ipv4 et le range de l'iptype ne\
            correspondent pas!")
        return

    def save(self, *args, **kwargs):
        self.clean()
        super(IpList, self).save(*args, **kwargs)

    def get_instance(iplistid, *args, **kwargs):
        """Récupère une instance
        :param iplistid: Instance id à trouver
        :return: Une instance iplist évidemment"""
        return IpList.objects.get(pk=iplistid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        une ip
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_iplist'), u"Vous n'avez pas le droit\
            de créer une ip"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance ip
        :param self: Instance ip à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_iplist'):
            return False, u"Vous n'avez pas le droit d'éditer des enregistrements ip"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour delete
        cette instance ip
        :param self: Instance ip à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.delete_iplist'):
            return False, u"Vous n'avez pas le droit d'éditer des enregistrements ip"
        return True, None

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des ip,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_iplist'):
            return False, u"Vous n'avez pas le droit de voir des enregistrements ip"
        return True, None

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit infra
        :param self: instance iplist à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_iplist'):
            return False, u"Vous n'avez pas le droit de voir des enregistrements ip"
        return True, None

    def __str__(self):
        return self.ipv4


class Service(models.Model):
    """ Definition d'un service (dhcp, dns, etc)"""
    PRETTY_NAME = "Services à générer (dhcp, dns, etc)"

    service_type = models.CharField(max_length=255, blank=True, unique=True)
    min_time_regen = models.DurationField(
        default=timedelta(minutes=1),
        help_text="Temps minimal avant nouvelle génération du service"
    )
    regular_time_regen = models.DurationField(
        default=timedelta(hours=1),
        help_text="Temps maximal avant nouvelle génération du service"
    )
    servers = models.ManyToManyField('Interface', through='Service_link')

    class Meta:
        permissions = (
            ("view_service", "Peut voir un objet service"),
        )

    def ask_regen(self):
        """ Marque à True la demande de régénération pour un service x """
        Service_link.objects.filter(service=self).exclude(asked_regen=True)\
            .update(asked_regen=True)
        return

    def process_link(self, servers):
        """ Django ne peut créer lui meme les relations manytomany avec table
        intermediaire explicite"""
        for serv in servers.exclude(
                pk__in=Interface.objects.filter(service=self)
            ):
            link = Service_link(service=self, server=serv)
            link.save()
        Service_link.objects.filter(service=self).exclude(server__in=servers)\
            .delete()
        return

    def save(self, *args, **kwargs):
        super(Service, self).save(*args, **kwargs)

    def get_instance(serviceid, *args, **kwargs):
        """Récupère une instance
        :param serviceid: Instance id à trouver
        :return: Une instance service évidemment"""
        return Service.objects.get(pk=serviceid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un service
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_service'), u"Vous n'avez pas le droit\
            de créer un service"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance service
        :param self: Instance service à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_service'):
            return False, u"Vous n'avez pas le droit d'éditer des services"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour delete
        cette instance service
        :param self: Instance service à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.delete_service'), u"Vous n'avez pas le droit\
            de supprimer un service"

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des services,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_service'), u"Vous n'avez pas le droit\
            de voir des services"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance service à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_service'), u"Vous n'avez pas le droit\
            de voir des services"

    def __str__(self):
        return str(self.service_type)


def regen(service):
    """ Fonction externe pour régérération d'un service, prend un objet service
    en arg"""
    obj = Service.objects.filter(service_type=service)
    if obj:
        obj[0].ask_regen()
    return


class Service_link(models.Model):
    """ Definition du lien entre serveurs et services"""
    PRETTY_NAME = "Relation entre service et serveur"

    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    server = models.ForeignKey('Interface', on_delete=models.CASCADE)
    last_regen = models.DateTimeField(auto_now_add=True)
    asked_regen = models.BooleanField(default=False)

    def done_regen(self):
        """ Appellé lorsqu'un serveur a regénéré son service"""
        self.last_regen = timezone.now()
        self.asked_regen = False
        self.save()

    def need_regen(self):
        """ Décide si le temps minimal écoulé est suffisant pour provoquer une
        régénération de service"""
        return bool(
            (self.asked_regen and (
                self.last_regen + self.service.min_time_regen
            ) < timezone.now()
            ) or (
                self.last_regen + self.service.regular_time_regen
            ) < timezone.now()
        )

    def get_instance(servicelinkid, *args, **kwargs):
        """Récupère une instance
        :param servicelinkid: Instance id à trouver
        :return: Une instance servicelink évidemment"""
        return ServiceLink.objects.get(pk=servicelinkid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un servicelink
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_service'), u"Vous n'avez pas le droit\
            de créer un service"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance servicelink
        :param self: Instance servicelink à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_service'):
            return False, u"Vous n'avez pas le droit d'éditer des services"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour delete
        cette instance servicelink
        :param self: Instance servicelink à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.delete_service'):
            return False, u"Vous n'avez pas le droit d'éditer des services"
        return True, None

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des services,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_service'), u"Vous n'avez pas le droit\
            de voir des liens de services"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance service à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_service'), u"Vous n'avez pas le droit\
            de voir des liens de services"

    def __str__(self):
        return str(self.server) + " " + str(self.service)


class OuverturePortList(models.Model):
    """Liste des ports ouverts sur une interface."""
    PRETTY_NAME = "Profil d'ouverture de ports"

    name = models.CharField(
        help_text="Nom de la configuration des ports.",
        max_length=255
    )

    class Meta:
        permissions = (
            ("view_ouvertureportlist", "Peut voir un objet ouvertureport"),
        )

    def get_instance(ouvertureportlistid, *args, **kwargs):
        """Récupère une instance
        :param ouvertureportlistid: Instance id à trouver
        :return: Une instance ouvertureportlist évidemment"""
        return OuverturePortList.objects.get(pk=ouvertureportlistid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits bureau pour créer
        une ouverture de port
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_ouvertureportlist') , u"Vous n'avez pas le droit\
            d'ouvrir un port"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits bureau pour editer
        cette instance ouvertureportlist
        :param self: Instance ouvertureportlist à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_ouvertureportlist'):
            return False, u"Vous n'avez pas le droit d'éditer des ouvertures de port"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits bureau pour delete
        cette instance ouvertureportlist
        :param self: Instance ouvertureportlist à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.delete_ouvertureportlist'):
            return False, u"Vous n'avez pas le droit de supprimer une ouverture\
                de port"
        if self.interface_set.all():
            return False, u"Cette liste de ports est utilisée"
        return True, None

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des ouvertureport,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_ouvertureportlist'), u"Vous n'avez pas le droit\
            de voir des ouverture de ports"

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance ouvertureport à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm('machines.view_ouvertureportlist'), u"Vous n'avez pas le droit\
            de voir des ouverture de ports"

    def __str__(self):
        return self.name

    def tcp_ports_in(self):
        """Renvoie la liste des ports ouverts en TCP IN pour ce profil"""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.TCP,
            io=OuverturePort.IN
        )

    def udp_ports_in(self):
        """Renvoie la liste des ports ouverts en UDP IN pour ce profil"""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.UDP,
            io=OuverturePort.IN
        )

    def tcp_ports_out(self):
        """Renvoie la liste des ports ouverts en TCP OUT pour ce profil"""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.TCP,
            io=OuverturePort.OUT
        )

    def udp_ports_out(self):
        """Renvoie la liste des ports ouverts en UDP OUT pour ce profil"""
        return self.ouvertureport_set.filter(
            protocole=OuverturePort.UDP,
            io=OuverturePort.OUT
        )


class OuverturePort(models.Model):
    """
    Représente un simple port ou une plage de ports.

    Les ports de la plage sont compris entre begin et en inclus.
    Si begin == end alors on ne représente qu'un seul port.

    On limite les ports entre 0 et 65535, tels que défini par la RFC
    """
    PRETTY_NAME = "Plage de port ouverte"

    TCP = 'T'
    UDP = 'U'
    IN = 'I'
    OUT = 'O'
    begin = models.PositiveIntegerField(validators=[MaxValueValidator(65535)])
    end = models.PositiveIntegerField(validators=[MaxValueValidator(65535)])
    port_list = models.ForeignKey(
        'OuverturePortList',
        on_delete=models.CASCADE
    )
    protocole = models.CharField(
        max_length=1,
        choices=(
            (TCP, 'TCP'),
            (UDP, 'UDP'),
            ),
        default=TCP,
    )
    io = models.CharField(
        max_length=1,
        choices=(
            (IN, 'IN'),
            (OUT, 'OUT'),
            ),
        default=OUT,
    )

    def get_instance(ouvertureportid, *args, **kwargs):
        """Récupère une instance
        :param ouvertureportid: Instance id à trouver
        :return: Une instance ouvertureport évidemment"""
        return OuverturePort.objects.get(pk=ouvertureportid)

    def can_create(user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits bureau pour créer
        une ouverture de port
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm('machines.add_ouvertureportlist') , u"Vous n'avez pas le droit\
            d'ouvrir un port"

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits bureau pour editer
        cette instance ouvertureport
        :param self: Instance ouvertureport à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.change_ouvertureportlist'):
            return False, u"Vous n'avez pas le droit d'éditer des ouvertures de port"
        return True, None

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits bureau pour delete
        cette instance ouvertureport
        :param self: Instance ouvertureport à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        if not user_request.has_perm('machines.delete_ouvertureportlist'):
            return False, u"Vous n'avez pas le droit d'éditer des ouvertures de port"
        return True, None

    def can_view_all(user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des ouvertureport,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_ouvertureportlist'):
            return False, u"Vous n'avez pas le droit d'éditer des ouvertures de port"
        return True, None

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance ouvertureport à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        if not user_request.has_perm('machines.view_ouvertureportlist'):
            return False, u"Vous n'avez pas le droit d'éditer des ouvertures de port"
        return True, None


    def __str__(self):
        if self.begin == self.end:
            return str(self.begin)
        return '-'.join([str(self.begin), str(self.end)])

    def show_port(self):
        """Formatage plus joli, alias pour str"""
        return str(self)


@receiver(post_save, sender=Machine)
def machine_post_save(sender, **kwargs):
    """Synchronisation ldap et régen parefeu/dhcp lors de la modification
    d'une machine"""
    user = kwargs['instance'].user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)
    regen('dhcp')
    regen('mac_ip_list')


@receiver(post_delete, sender=Machine)
def machine_post_delete(sender, **kwargs):
    """Synchronisation ldap et régen parefeu/dhcp lors de la suppression
    d'une machine"""
    machine = kwargs['instance']
    user = machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)
    regen('dhcp')
    regen('mac_ip_list')


@receiver(post_save, sender=Interface)
def interface_post_save(sender, **kwargs):
    """Synchronisation ldap et régen parefeu/dhcp lors de la modification
    d'une interface"""
    interface = kwargs['instance']
    interface.sync_ipv6_slaac()
    user = interface.machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)
    # Regen services
    regen('dhcp')
    regen('mac_ip_list')


@receiver(post_delete, sender=Interface)
def interface_post_delete(sender, **kwargs):
    """Synchronisation ldap et régen parefeu/dhcp lors de la suppression
    d'une interface"""
    interface = kwargs['instance']
    user = interface.machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)


@receiver(post_save, sender=IpType)
def iptype_post_save(sender, **kwargs):
    """Generation des objets ip après modification d'un range ip"""
    iptype = kwargs['instance']
    iptype.gen_ip_range()


@receiver(post_save, sender=MachineType)
def machine_post_save(sender, **kwargs):
    """Mise à jour des interfaces lorsque changement d'attribution
    d'une machinetype (changement iptype parent)"""
    machinetype = kwargs['instance']
    for interface in machinetype.all_interfaces():
        interface.update_type()


@receiver(post_save, sender=Domain)
def domain_post_save(sender, **kwargs):
    """Regeneration dns après modification d'un domain object"""
    regen('dns')


@receiver(post_delete, sender=Domain)
def domain_post_delete(sender, **kwargs):
    """Regeneration dns après suppression d'un domain object"""
    regen('dns')


@receiver(post_save, sender=Extension)
def extension_post_save(sender, **kwargs):
    """Regeneration dns après modification d'une extension"""
    regen('dns')


@receiver(post_delete, sender=Extension)
def extension_post_selete(sender, **kwargs):
    """Regeneration dns après suppression d'une extension"""
    regen('dns')


@receiver(post_save, sender=SOA)
def soa_post_save(sender, **kwargs):
    """Regeneration dns après modification d'un SOA"""
    regen('dns')


@receiver(post_delete, sender=SOA)
def soa_post_delete(sender, **kwargs):
    """Regeneration dns après suppresson d'un SOA"""
    regen('dns')


@receiver(post_save, sender=Mx)
def mx_post_save(sender, **kwargs):
    """Regeneration dns après modification d'un MX"""
    regen('dns')


@receiver(post_delete, sender=Mx)
def mx_post_delete(sender, **kwargs):
    """Regeneration dns après suppresson d'un MX"""
    regen('dns')


@receiver(post_save, sender=Ns)
def ns_post_save(sender, **kwargs):
    """Regeneration dns après modification d'un NS"""
    regen('dns')


@receiver(post_delete, sender=Ns)
def ns_post_delete(sender, **kwargs):
    """Regeneration dns après modification d'un NS"""
    regen('dns')


@receiver(post_save, sender=Txt)
def text_post_save(sender, **kwargs):
    """Regeneration dns après modification d'un TXT"""
    regen('dns')


@receiver(post_delete, sender=Txt)
def text_post_delete(sender, **kwargs):
    """Regeneration dns après modification d'un TX"""
    regen('dns')


@receiver(post_save, sender=Srv)
def srv_post_save(sender, **kwargs):
    """Regeneration dns après modification d'un SRV"""
    regen('dns')


@receiver(post_delete, sender=Srv)
def text_post_delete(sender, **kwargs):
    """Regeneration dns après modification d'un SRV"""
    regen('dns')

