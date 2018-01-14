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

"""Handles ACL for re2o.

Here are defined some decorators that can be used in views to handle ACL.
"""
from __future__ import unicode_literals

import sys

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

import cotisations, logs, machines, preferences, search, topologie, users


def can_create(model):
    """Decorator to check if an user can create a model.
    It assumes that a valid user exists in the request and that the model has a
    method can_create(user) which returns true if the user can create this kind
    of models.
    """
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            can, msg = model.can_create(request.user, *args, **kwargs)
            #options, _created = OptionalUser.objects.get_or_create()
            if not can:
                messages.error(request, msg or "Vous ne pouvez pas accéder à ce menu")
                return redirect(reverse('index'))
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def can_edit(model, *field_list):
    """Decorator to check if an user can edit a model.
    It tries to get an instance of the model, using
    `model.get_instance(*args, **kwargs)` and assumes that the model has a
    method `can_edit(user)` which returns `true` if the user can edit this
    kind of models.
    """
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            try:
                instance = model.get_instance(*args, **kwargs)
            except model.DoesNotExist:
                messages.error(request, u"Entrée inexistante")
                return redirect(reverse('users:profil',
                    kwargs={'userid':str(request.user.id)}
                ))
            can, msg = instance.can_edit(request.user)
            if not can:
                messages.error(request, msg or "Vous ne pouvez pas accéder à ce menu")
                return redirect(reverse('users:profil',
                    kwargs={'userid':str(request.user.id)}
                ))
            for field in field_list:
                can_change = getattr(instance, 'can_change_' + field)
                can, msg = can_change(request.user, *args, **kwargs)
                if not can:
                    messages.error(request, msg or "Vous ne pouvez pas accéder à ce menu")
                    return redirect(reverse('users:profil',
                        kwargs={'userid':str(request.user.id)}
                    ))
            return view(request, instance, *args, **kwargs)
        return wrapper
    return decorator


def can_change(model, *field_list):
    """Decorator to check if an user can edit a field of a model class.
    Difference with can_edit : take a class and not an instance
    """
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            for field in field_list:
                can_change = getattr(model, 'can_change_' + field)
                can, msg = can_change(request.user, *args, **kwargs)
                if not can:
                    messages.error(request, msg or "Vous ne pouvez pas accéder à ce menu")
                    return redirect(reverse('users:profil',
                        kwargs={'userid':str(request.user.id)}
                    ))
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def can_delete(model):
    """Decorator to check if an user can delete a model.
    It tries to get an instance of the model, using
    `model.get_instance(*args, **kwargs)` and assumes that the model has a
    method `can_delete(user)` which returns `true` if the user can delete this
    kind of models.
    """
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            try:
                instance = model.get_instance(*args, **kwargs)
            except model.DoesNotExist:
                messages.error(request, u"Entrée inexistante")
                return redirect(reverse('users:profil',
                    kwargs={'userid':str(request.user.id)}
                ))
            can, msg = instance.can_delete(request.user)
            if not can:
                messages.error(request, msg or "Vous ne pouvez pas accéder à ce menu")
                return redirect(reverse('users:profil',
                    kwargs={'userid':str(request.user.id)}
                ))
            return view(request, instance, *args, **kwargs)
        return wrapper
    return decorator


def can_delete_set(model):
    """Decorator which returns a list of detable models by request user.
    If none of them, return an error"""
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            all_objects = model.objects.all()
            instances_id = []
            for instance in all_objects:
                can, msg = instance.can_delete(request.user)
                if can:
                    instances_id.append(instance.id)
            instances = model.objects.filter(id__in=instances_id)
            if not instances:
                messages.error(request, "Vous ne pouvez pas accéder à ce menu")
                return redirect(reverse('users:profil',
                    kwargs={'userid':str(request.user.id)}
                ))
            return view(request, instances, *args, **kwargs)
        return wrapper
    return decorator


def can_view(model):
    """Decorator to check if an user can view a model.
    It tries to get an instance of the model, using
    `model.get_instance(*args, **kwargs)` and assumes that the model has a
    method `can_view(user)` which returns `true` if the user can view this
    kind of models.
    """
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            try:
                instance = model.get_instance(*args, **kwargs)
            except model.DoesNotExist:
                messages.error(request, u"Entrée inexistante")
                return redirect(reverse('users:profil',
                    kwargs={'userid':str(request.user.id)}
                ))
            can, msg = instance.can_view(request.user)
            if not can:
                messages.error(request, msg or "Vous ne pouvez pas accéder à ce menu")
                return redirect(reverse('users:profil',
                    kwargs={'userid':str(request.user.id)}
                ))
            return view(request, instance, *args, **kwargs)
        return wrapper
    return decorator


def can_view_all(model):
    """Decorator to check if an user can view a class of model.
    """
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            can, msg = model.can_view_all(request.user)
            if not can:
                messages.error(request, msg or "Vous ne pouvez pas accéder à ce menu")
                return redirect(reverse('users:profil',
                    kwargs={'userid':str(request.user.id)}
                ))
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def can_view_app(app_name):
    """Decorator to check if an user can view an application.
    """
    assert app_name in sys.modules.keys()
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            app = sys.modules[app_name]
            can,msg = app.can_view(request.user)
            if can:
                return view(request, *args, **kwargs)
            messages.error(request, msg)
            return redirect(reverse('users:profil',
                kwargs={'userid':str(request.user.id)}
            ))
        return wrapper
    return decorator


def can_edit_history(view):
    """Decorator to check if an user can edit history."""
    def wrapper(request, *args, **kwargs):
        if request.user.has_perm('admin.change_logentry'):
            return view(request, *args, **kwargs)
        messages.error(
           request,
           "Vous ne pouvez pas éditer l'historique."
        )
        return redirect(reverse('users:profil',
            kwargs={'userid':str(request.user.id)}
        ))
    return wrapper

