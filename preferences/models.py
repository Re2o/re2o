# -*- mode: python; coding: utf-8 -*-
# Re2o un logiciel d'administration développé initiallement au rezometz. Il
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
"""
Reglages généraux, machines, utilisateurs, mail, general pour l'application.
"""
from __future__ import unicode_literals

from django.db import models
import cotisations.models


class OptionalUser(models.Model):
    """Options pour l'user : obligation ou nom du telephone,
    activation ou non du solde, autorisation du negatif, fingerprint etc"""
    PRETTY_NAME = "Options utilisateur"

    is_tel_mandatory = models.BooleanField(default=True)
    user_solde = models.BooleanField(default=False)
    solde_negatif = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    max_solde = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50
    )
    gpg_fingerprint = models.BooleanField(default=True)
    all_can_create = models.BooleanField(
        default=False,
        help_text="Tous les users peuvent en créer d'autres",
    )

    class Meta:
        permissions = (
            ("view_optionaluser", "Peut voir les options de l'user"),
        )

    def get_instance(*args, **kwargs):
        return OptionalUser.objects.get_or_create()

    def can_create(user_request, *args, **kwargs):
        """Check if an user can create a OptionalUser object.

        :param user_request: The user who wants to create a user object.
        :return: a message and a boolean which is True if the user can create.
        """
        return user_request.has_perm('preferences.add_optionaluser'), u"Vous n'avez pas le droit\
            de créer les préférences concernant les users"

    def can_edit(self, user_request, *args, **kwargs):
        """Check if an user can edit a OptionalUser object.

        :param self: The OptionalUser which is to be edited.
        :param user_request: The user who requests to edit self.
        :return: a message and a boolean which is True if edition is granted.
        """
        return user_request.has_perm('preferences.change_optionaluser'), u"Vous n'avez pas le droit\
            d'éditer les préférences concernant les users"

    def can_delete(self, user_request, *args, **kwargs):
        """Check if an user can delete a OptionalUser object.

        :param self: The OptionalUser which is to be deleted.
        :param user_request: The user who requests deletion.
        :return: True if deletion is granted, and a message.
        """
        return user_request.has_perm('preferences.delete_optionaluser'), u"Vous n'avez pas le droit\
            de supprimer les préférences concernant les users"

    def can_view_all(user_request, *args, **kwargs):
        """Check if an user can access to the list of every OptionalUser objects

        :param user_request: The user who wants to view the list.
        :return: True if the user can view the list and an explanation message.
        """
        return user_request.has_perm('preferences.view_optionaluser'), u"Vous n'avez pas le droit\
            de voir les préférences concernant les utilisateurs"

    def can_view(self, user_request, *args, **kwargs):
        """Check if an user can view a OptionalUser object.

        :param self: The targeted OptionalUser.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
        text
        """
        return user_request.has_perm('preferences.view_optionaluser'), u"Vous n'avez pas le droit\
            de voir les préférences concernant les utilisateurs"

    def clean(self):
        """Creation du mode de paiement par solde"""
        if self.user_solde:
            p = cotisations.models.Paiement.objects.filter(moyen="Solde")
            if not len(p):
                c = cotisations.models.Paiement(moyen="Solde")
                c.save()


class OptionalMachine(models.Model):
    """Options pour les machines : maximum de machines ou d'alias par user
    sans droit, activation de l'ipv6"""
    PRETTY_NAME = "Options machines"

    password_machine = models.BooleanField(default=False)
    max_lambdauser_interfaces = models.IntegerField(default=10)
    max_lambdauser_aliases = models.IntegerField(default=10)
    ipv6 = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("view_optionalmachine", "Peut voir les options de machine"),
        )

    def get_instance(*args, **kwargs):
        return OptionalMachine.objects.get_or_create()

    def can_create(user_request, *args, **kwargs):
        """Check if an user can create a OptionalMachine object.

        :param user_request: The user who wants to create an object.
        :return: a message and a boolean which is True if the user can create.
        """
        return user_request.has_perm('preferences.add_optionalmachine'), u"Vous n'avez pas le droit\
            de créer les préférences concernant les machines"

    def can_edit(self, user_request, *args, **kwargs):
        """Check if an user can edit a OptionalMachine object.

        :param self: The OptionalMachine which is to be edited.
        :param user_request: The user who requests to edit self.
        :return: a message and a boolean which is True if edition is granted.
        """
        return user_request.has_perm('preferences.change_optionalmachine'), u"Vous n'avez pas le droit\
            d'éditer les préférences concernant les machines"

    def can_delete(self, user_request, *args, **kwargs):
        """Check if an user can delete a OptionalMachine object.

        :param self: The OptionalMachine which is to be deleted.
        :param user_request: The user who requests deletion.
        :return: True if deletion is granted, and a message.
        """

        return user_request.has_perm('preferences.delete_optionalmachine'), u"Vous n'avez pas le droit\
            de supprimer les préférences concernant les machines"

    def can_view_all(user_request, *args, **kwargs):
        """Check if an user can access to the list of every OptionalMachine objects

        :param user_request: The user who wants to view the list.
        :return: True if the user can view the list and an explanation message.
        """
        return user_request.has_perm('preferences.view_optionalmachine'), u"Vous n'avez pas le droit\
            de voir les préférences concernant les machines"

    def can_view(self, user_request, *args, **kwargs):
        """Check if an user can view a OptionalMachine object.

        :param self: The targeted OptionalMachine.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
        text
        """
        return user_request.has_perm('preferences.view_optionalmachine'), u"Vous n'avez pas le droit\
            de voir les préférences concernant les machines"


class OptionalTopologie(models.Model):
    """Reglages pour la topologie : mode d'accès radius, vlan où placer
    les machines en accept ou reject"""
    PRETTY_NAME = "Options topologie"
    MACHINE = 'MACHINE'
    DEFINED = 'DEFINED'
    CHOICE_RADIUS = (
        (MACHINE, 'Sur le vlan de la plage ip machine'),
        (DEFINED, 'Prédéfini dans "Vlan où placer les machines\
            après acceptation RADIUS"'),
    )

    radius_general_policy = models.CharField(
        max_length=32,
        choices=CHOICE_RADIUS,
        default='DEFINED'
    )
    vlan_decision_ok = models.OneToOneField(
        'machines.Vlan',
        on_delete=models.PROTECT,
        related_name='decision_ok',
        blank=True,
        null=True
    )
    vlan_decision_nok = models.OneToOneField(
        'machines.Vlan',
        on_delete=models.PROTECT,
        related_name='decision_nok',
        blank=True,
        null=True
    )

    class Meta:
        permissions = (
            ("view_optionaltopologie", "Peut voir les options de topologie"),
        )

    def get_instance(*args, **kwargs):
        return OptionalTopologie.objects.get_or_create()

    def can_create(user_request, *args, **kwargs):
        """Check if an user can create a OptionalTopologie object.

        :param user_request: The user who wants to create an object.
        :return: a message and a boolean which is True if the user can create.
        """
        return user_request.has_perm('preferences.add_optionaltopologie'), u"Vous n'avez pas le droit\
            de créer les préférences concernant la topologie"

    def can_edit(self, user_request, *args, **kwargs):
        """Check if an user can edit a OptionalTopologie object.

        :param self: The OptionalTopologie which is to be edited.
        :param user_request: The user who requests to edit self.
        :return: a message and a boolean which is True if edition is granted.
        """
        return user_request.has_perm('preferences.change_optionaltopologie'), u"Vous n'avez pas le droit\
            d'éditer les préférences concernant la topologie"

    def can_delete(self, user_request, *args, **kwargs):
        """Check if an user can delete a OptionalTopologie object.

        :param self: The OptionalTopologie which is to be deleted.
        :param user_request: The user who requests deletion.
        :return: True if deletion is granted, and a message.
        """
        return user_request.has_perm('preferences.delete_optionaltoplogie'), u"Vous n'avez pas le droit\
            d'éditer les préférences concernant la topologie"

    def can_view_all(user_request, *args, **kwargs):
        """Check if an user can access to the list of every OptionalTopologie objects

        :param user_request: The user who wants to view the list.
        :return: True if the user can view the list and an explanation message.
        """
        return user_request.has_perm('preferences.view_optionaltopologie'), u"Vous n'avez pas le droit\
            de voir les préférences concernant la topologie"

    def can_view(self, user_request, *args, **kwargs):
        """Check if an user can view a OptionalTopologie object.

        :param self: The targeted OptionalTopologie.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
        text
        """
        return user_request.has_perm('preferences.view_optionaltopologie'), u"Vous n'avez pas le droit\
            de voir les préférences concernant la topologie"


class GeneralOption(models.Model):
    """Options générales : nombre de resultats par page, nom du site,
    temps où les liens sont valides"""
    PRETTY_NAME = "Options générales"

    general_message = models.TextField(
        default="",
        blank=True,
        help_text="Message général affiché sur le site (maintenance, etc"
    )
    search_display_page = models.IntegerField(default=15)
    pagination_number = models.IntegerField(default=25)
    pagination_large_number = models.IntegerField(default=8)
    req_expire_hrs = models.IntegerField(default=48)
    site_name = models.CharField(max_length=32, default="Re2o")
    email_from = models.EmailField(default="www-data@serveur.net")

    class Meta:
        permissions = (
            ("view_generaloption", "Peut voir les options générales"),
        )

    def get_instance(*args, **kwargs):
        return GeneralOption.objects.get_or_create()

    def can_create(user_request, *args, **kwargs):
        """Check if an user can create a GeneralOption object.

        :param user_request: The user who wants to create an object.
        :return: a message and a boolean which is True if the user can create.
        """
        return user_request.has_perm('preferences.add_generaloption'), u"Vous n'avez pas le droit\
            de créer les préférences générales"

    def can_edit(self, user_request, *args, **kwargs):
        """Check if an user can edit a GeneralOption object.

        :param self: The GeneralOption which is to be edited.
        :param user_request: The user who requests to edit self.
        :return: a message and a boolean which is True if edition is granted.
        """
        return user_request.has_perm('preferences.change_generaloption'), u"Vous n'avez pas le droit\
            d'éditer les préférences générales"

    def can_delete(self, user_request, *args, **kwargs):
        """Check if an user can delete a GeneralOption object.

        :param self: The GeneralOption which is to be deleted.
        :param user_request: The user who requests deletion.
        :return: True if deletion is granted, and a message.
        """
        return user_request.has_perm('preferences.delete_generaloption'), u"Vous n'avez pas le droit\
            d'éditer les préférences générales"

    def can_view_all(user_request, *args, **kwargs):
        """Check if an user can access to the list of every GeneralOption objects

        :param user_request: The user who wants to view the list.
        :return: True if the user can view the list and an explanation message.
        """

        return user_request.has_perm('preferences.view_generaloption'), u"Vous n'avez pas le droit\
            de voir les préférences générales"

    def can_view(self, user_request, *args, **kwargs):
        """Check if an user can view a GeneralOption object.

        :param self: The targeted GeneralOption.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
        text
        """
        return user_request.has_perm('preferences.view_generaloption'), u"Vous n'avez pas le droit\
            de voir les préférences générales"


class Service(models.Model):
    """Liste des services affichés sur la page d'accueil : url, description,
    image et nom"""
    name = models.CharField(max_length=32)
    url = models.URLField()
    description = models.TextField()
    image = models.ImageField(upload_to='logo', blank=True)

    class Meta:
        permissions = (
            ("view_service", "Peut voir les options de service"),
        )

    def get_instance(serviceid, *args, **kwargs):
        return Service.objects.get(pk=serviceid)

    def can_create(user_request, *args, **kwargs):
        """Check if an user can create a Service object.

        :param user_request: The user who wants to create an object.
        :return: a message and a boolean which is True if the user can create.
        """

        return user_request.has_perm('preferences.add_service'), u"Vous n'avez pas le droit\
            de créer un service pour la page d'accueil"

    def can_edit(self, user_request, *args, **kwargs):
        """Check if an user can edit a Service object.

        :param self: The Service which is to be edited.
        :param user_request: The user who requests to edit self.
        :return: a message and a boolean which is True if edition is granted.
        """
        return user_request.has_perm('preferences.change_service'), u"Vous n'avez pas le droit\
            d'éditer les services pour la page d'accueil"

    def can_delete(self, user_request, *args, **kwargs):
        """Check if an user can delete a Service object.

        :param self: The Right which is to be deleted.
        :param user_request: The user who requests deletion.
        :return: True if deletion is granted, and a message.
        """
        return user_request.has_perm('preferences.delete_service'), u"Vous n'avez pas le droit\
            de supprimer les services pour la page d'accueil"

    def can_view_all(user_request, *args, **kwargs):
        """Check if an user can access to the list of every Service objects

        :param user_request: The user who wants to view the list.
        :return: True if the user can view the list and an explanation message.
        """

        return user_request.has_perm('preferences.view_service'), u"Vous n'avez pas le droit\
            de voir les services pour la page d'accueil"

    def can_view(self, user_request, *args, **kwargs):
        """Check if an user can view a Service object.

        :param self: The targeted Service.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
        text
        """
        return user_request.has_perm('preferences.view_service'), u"Vous n'avez pas le droit\
            de voir les services pour la page d'accueil"

    def __str__(self):
        return str(self.name)


class AssoOption(models.Model):
    """Options générales de l'asso : siret, addresse, nom, etc"""
    PRETTY_NAME = "Options de l'association"

    name = models.CharField(
        default="Association réseau école machin",
        max_length=256
    )
    siret = models.CharField(default="00000000000000", max_length=32)
    adresse1 = models.CharField(default="1 Rue de exemple", max_length=128)
    adresse2 = models.CharField(default="94230 Cachan", max_length=128)
    contact = models.EmailField(default="contact@example.org")
    telephone = models.CharField(max_length=15, default="0000000000")
    pseudo = models.CharField(default="Asso", max_length=32)
    utilisateur_asso = models.OneToOneField(
        'users.User',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    PAYMENT = (
        ('NONE', 'NONE'),
        ('COMNPAY', 'COMNPAY'),
    )
    payment = models.CharField(max_length=255,
        choices=PAYMENT,
        default='NONE',
    )
    class Meta:
        permissions = (
            ("view_assooption", "Peut voir les options de l'asso"),
        )

    def get_instance(*args, **kwargs):
        return AssoOption.objects.get_or_create()

    def can_create(user_request, *args, **kwargs):
        """Check if an user can create a AssoOption object.

        :param user_request: The user who wants to create an object.
        :return: a message and a boolean which is True if the user can create.
        """
        return user_request.has_perm('preferences.add_assooption'), u"Vous n'avez pas le droit\
            d'éditer les préférences concernant l'association"

    def can_edit(self, user_request, *args, **kwargs):
        """Check if an user can edit a AssoOption object.

        :param self: The AssoOption which is to be edited.
        :param user_request: The user who requests to edit self.
        :return: a message and a boolean which is True if edition is granted.
        """
        return user_request.has_perm('preferences.change_assooption'), u"Vous n'avez pas le droit\
            d'éditer les préférences concernant l'association"

    def can_delete(self, user_request, *args, **kwargs):
        """Check if an user can delete a AssoOption object.

        :param self: The AssoOption which is to be deleted.
        :param user_request: The user who requests deletion.
        :return: True if deletion is granted, and a message.
        """
        return user_request.has_perm('preferences.delete_assooption'), u"Vous n'avez pas le droit\
            d'éditer les préférences concernant l'association"

    def can_view_all(user_request, *args, **kwargs):
        """Check if an user can access to the list of every AssoOption objects

        :param user_request: The user who wants to view the list.
        :return: True if the user can view the list and an explanation message.
        """
        return user_request.has_perm('preferences.view_assooption'), u"Vous n'avez pas le droit\
            de voir les préférences concernant l'association"

    def can_view(self, user_request, *args, **kwargs):
        """Check if an user can view a AssoOption object.

        :param self: The targeted AssoOption.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
        text
        """
        return user_request.has_perm('preferences.view_assooption'), u"Vous n'avez pas le droit\
            de voir les préférences concernant l'association"


class MailMessageOption(models.Model):
    """Reglages, mail de bienvenue et autre"""
    PRETTY_NAME = "Options de corps de mail"

    welcome_mail_fr = models.TextField(default="")
    welcome_mail_en = models.TextField(default="")

    class Meta:
        permissions = (
            ("view_mailmessageoption", "Peut voir les options de mail"),
        )

    def get_instance(*args, **kwargs):
        return MailMessageOption.objects.get_or_create()

    def can_create(user_request, *args, **kwargs):
        """Check if an user can create a MailMessageOption object.

        :param user_request: The user who wants to create an object.
        :return: a message and a boolean which is True if the user can create.
        """
        return user_request.has_perm('preferences.add_mailmessageoption'), u"Vous n'avez pas le droit\
            d'éditer les préférences concernant les mails"

    def can_edit(self, user_request, *args, **kwargs):
        """Check if an user can edit a MailMessageOption object.

        :param self: The MailMessageOption which is to be edited.
        :param user_request: The user who requests to edit self.
        :return: a message and a boolean which is True if edition is granted.
        """

        return user_request.has_perm('preferences.change_mailmessageoption'), u"Vous n'avez pas le droit\
            d'éditer les préférences concernant les mails"

    def can_delete(self, user_request, *args, **kwargs):
        """Check if an user can delete a AssoOption object.

        :param self: The AssoOption which is to be deleted.
        :param user_request: The user who requests deletion.
        :return: True if deletion is granted, and a message.
        """
        return user_request.has_perm('preferences.delete_mailmessageoption'), u"Vous n'avez pas le droit\
            d'éditer les préférences concernant les mails"

    def can_view_all(user_request, *args, **kwargs):
        """Check if an user can access to the list of every AssoOption objects

        :param user_request: The user who wants to view the list.
        :return: True if the user can view the list and an explanation message.
        """
        return user_request.has_perm('preferences.view_mailmessageoption'), u"Vous n'avez pas le droit\
            de voir les préférences concernant les mails"

    def can_view(self, user_request, *args, **kwargs):
        """Check if an user can view a AssoOption object.

        :param self: The targeted AssoOption.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
        text
        """
        return user_request.has_perm('preferences.view_mailmessageoption'), u"Vous n'avez pas le droit\
            de voir les préférences concernant les mails"
