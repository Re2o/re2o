# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Gabriel Détraz
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

class AclMixin(object):
    @classmethod
    def get_classname(cls):
        return str(cls.__name__).lower()

    @classmethod
    def get_modulename(cls):
        return str(cls.__module__).split('.')[0].lower()

    @classmethod
    def get_instance(cls, *args, **kwargs):
        """Récupère une instance
        :param objectid: Instance id à trouver
        :return: Une instance de la classe évidemment"""
        object_id = kwargs.get(cls.get_classname() + 'id')
        return cls.objects.get(pk=object_id)

    @classmethod
    def can_create(cls, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour créer
        un servicelink
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm(cls.get_modulename() + '.add_' + cls.get_classname()), u"Vous n'avez pas le droit\
            de créer un " + cls.get_classname()

    def can_edit(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour editer
        cette instance servicelink
        :param self: Instance servicelink à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm(self.get_modulename() + '.change_' + self.get_classname()), u"Vous n'avez pas le droit d'éditer des " + self.get_classname()

    def can_delete(self, user_request, *args, **kwargs):
        """Verifie que l'user a les bons droits infra pour delete
        cette instance servicelink
        :param self: Instance servicelink à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return user_request.has_perm(self.get_modulename() + '.delete_' + self.get_classname()), u"Vous n'avez pas le droit d'éditer des " + self.get_classname()

    @classmethod
    def can_view_all(cls, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des services,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm(cls.get_modulename() + '.view_' + cls.get_classname()), u"Vous n'avez pas le droit de voir des " + cls.get_classname()

    def can_view(self, user_request, *args, **kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance service à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return user_request.has_perm(self.get_modulename() + '.view_' + self.get_classname()), u"Vous n'avez pas le droit de voir des " + self.get_classname()
