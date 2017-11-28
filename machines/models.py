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

import users.models
import preferences.models


class Machine(models.Model):
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

    def can_create(user_request, userid_dest):
        try:
            user = users.models.User.objects.get(pk=userid_dest)
        except users.models.User.DoesNotExist:
            return False, u"Utilisateur inexistant"
        options, created = preferences.models.OptionalMachine.objects.get_or_create()
        max_lambdauser_interfaces = options.max_lambdauser_interfaces
        if not user_request.has_perms(('cableur',)):
            if user != user_request:
                return False, u"Vous ne pouvez pas ajouter une machine à un\
                        autre user que vous sans droit"
            if user.user_interfaces().count() >= max_lambdauser_interfaces:
                return False, u"Vous avez atteint le maximum d'interfaces\
                        autorisées que vous pouvez créer vous même (%s) "\
                        % max_lambdauser_interfaces
        return True, None

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

    def all_interfaces(self):
        """ Renvoie toutes les interfaces (cartes réseaux) de type
        machinetype"""
        return Interface.objects.filter(type=self)

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

    def __str__(self):
        return self.type


class Vlan(models.Model):
    """ Un vlan : vlan_id et nom
    On limite le vlan id entre 0 et 4096, comme défini par la norme"""
    PRETTY_NAME = "Vlans"

    vlan_id = models.PositiveIntegerField(validators=[MaxValueValidator(4095)])
    name = models.CharField(max_length=256)
    comment = models.CharField(max_length=256, blank=True)

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

    def __str__(self):
        return self.name

    def clean(self):
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

    @cached_property
    def dns_entry(self):
        """Renvoie l'entrée DNS complète pour un MX à mettre dans les
        fichiers de zones"""
        return "@               IN  MX  " + str(self.priority).ljust(3) + " " + str(self.name)

    def __str__(self):
        return str(self.zone) + ' ' + str(self.priority) + ' ' + str(self.name)


class Ns(models.Model):
    """Liste des enregistrements name servers par zone considéérée"""
    PRETTY_NAME = "Enregistrements NS"

    zone = models.ForeignKey('Extension', on_delete=models.PROTECT)
    ns = models.OneToOneField('Domain', on_delete=models.PROTECT)

    @cached_property
    def dns_entry(self):
        """Renvoie un enregistrement NS complet pour les filezones"""
        return "@               IN  NS      " + str(self.ns)

    def __str__(self):
        return str(self.zone) + ' ' + str(self.ns)


class Txt(models.Model):
    """ Un enregistrement TXT associé à une extension"""
    PRETTY_NAME = "Enregistrement TXT"

    zone = models.ForeignKey('Extension', on_delete=models.PROTECT)
    field1 = models.CharField(max_length=255)
    field2 = models.TextField(max_length=2047)

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


class Interface(models.Model):
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

    @cached_property
    def is_active(self):
        """ Renvoie si une interface doit avoir accès ou non """
        machine = self.machine
        user = self.machine.user
        return machine.active and user.has_access()

    @cached_property
    def ipv6_object(self):
        """ Renvoie un objet type ipv6 à partir du prefix associé à
        l'iptype parent"""
        if self.type.ip_type.prefix_v6:
            return EUI(self.mac_address).ipv6(
                IPNetwork(self.type.ip_type.prefix_v6).network
            )
        else:
            return None

    @cached_property
    def ipv6(self):
        """ Renvoie l'ipv6 en str. Mise en cache et propriété de l'objet"""
        return str(self.ipv6_object)

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

    def __str__(self):
        return str(self.name) + str(self.extension)


class IpList(models.Model):
    PRETTY_NAME = "Addresses ipv4"

    ipv4 = models.GenericIPAddressField(protocol='IPv4', unique=True)
    ip_type = models.ForeignKey('IpType', on_delete=models.CASCADE)

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

    def __str__(self):
        return str(self.server) + " " + str(self.service)


class OuverturePortList(models.Model):
    """Liste des ports ouverts sur une interface."""
    PRETTY_NAME = "Profil d'ouverture de ports"

    name = models.CharField(
        help_text="Nom de la configuration des ports.",
        max_length=255
    )

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
