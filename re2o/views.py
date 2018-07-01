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
"""
Fonctions de la page d'accueil et diverses fonctions utiles pour tous
les views
"""

from __future__ import unicode_literals

from itertools import chain
import git
from reversion.models import Version

from django.http import Http404
from django.urls import reverse
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page

import preferences
from preferences.models import (
    Service,
    MailContact,
    GeneralOption,
    AssoOption,
    HomeOption
)
import users
import cotisations
import topologie
import machines

from .utils import re2o_paginator
from .contributors import CONTRIBUTORS


def form(ctx, template, request):
    """Form générique, raccourci importé par les fonctions views du site"""
    context = ctx
    context.update(csrf(request))
    return render(request, template, context)


def index(request):
    """Affiche la liste des services sur la page d'accueil de re2o"""
    services = [[], [], []]
    for indice, serv in enumerate(Service.objects.all()):
        services[indice % 3].append(serv)
    twitter_url = HomeOption.get_cached_value('twitter_url')
    facebook_url = HomeOption.get_cached_value('facebook_url')
    twitter_account_name = HomeOption.get_cached_value('twitter_account_name')
    asso_name = AssoOption.get_cached_value('pseudo')
    return form({
         'services_urls': services,
         'twitter_url': twitter_url,
         'twitter_account_name' : twitter_account_name,
         'facebook_url': facebook_url,
         'asso_name': asso_name
         }, 're2o/index.html', request)


#: Binding the corresponding char sequence of history url to re2o models.
HISTORY_BIND = {
    'users': {
        'user': users.models.User,
        'ban': users.models.Ban,
        'mailalias': users.models.MailAlias,
        'whitelist': users.models.Whitelist,
        'school': users.models.School,
        'listright': users.models.ListRight,
        'serviceuser': users.models.ServiceUser,
        'listshell': users.models.ListShell,
    },
    'preferences': {
        'service': preferences.models.Service,
        'mailcontact': preferences.models.MailContact,
    },
    'cotisations': {
        'facture': cotisations.models.Facture,
        'article': cotisations.models.Article,
        'paiement': cotisations.models.Paiement,
        'banque': cotisations.models.Banque,
    },
    'topologie': {
        'switch': topologie.models.Switch,
        'port': topologie.models.Port,
        'room': topologie.models.Room,
        'stack': topologie.models.Stack,
        'modelswitch': topologie.models.ModelSwitch,
        'constructorswitch': topologie.models.ConstructorSwitch,
        'accesspoint': topologie.models.AccessPoint,
        'switchbay': topologie.models.SwitchBay,
        'building': topologie.models.Building,
    },
    'machines': {
        'machine': machines.models.Machine,
        'interface': machines.models.Interface,
        'domain': machines.models.Domain,
        'machinetype': machines.models.MachineType,
        'iptype': machines.models.IpType,
        'extension': machines.models.Extension,
        'soa': machines.models.SOA,
        'mx': machines.models.Mx,
        'txt': machines.models.Txt,
        'dname': machines.models.DName,
        'srv': machines.models.Srv,
        'ns': machines.models.Ns,
        'service': machines.models.Service,
        'role': machines.models.Role,
        'vlan': machines.models.Vlan,
        'nas': machines.models.Nas,
        'ipv6list': machines.models.Ipv6List,
        'sshfingerprint': machines.models.SshFingerprint,
        'sshfpralgo': machines.models.SshFprAlgo,
    },
}


@login_required
def history(request, application, object_name, object_id):
    """Render history for a model.

    The model is determined using the `HISTORY_BIND` dictionnary if none is
    found, raises a Http404. The view checks if the user is allowed to see the
    history using the `can_view` method of the model.

    Args:
        request: The request sent by the user.
        object_name: Name of the model.
        object_id: Id of the object you want to acces history.

    Returns:
        The rendered page of history if access is granted, else the user is
        redirected to their profile page, with an error message.

    Raises:
        Http404: This kind of models doesn't have history.
    """
    try:
        model = HISTORY_BIND[application][object_name]
    except KeyError:
        raise Http404(u"Il n'existe pas d'historique pour ce modèle.")
    object_name_id = object_name + 'id'
    kwargs = {object_name_id: object_id}
    try:
        instance = model.get_instance(**kwargs)
    except model.DoesNotExist:
        messages.error(request, u"Entrée inexistante")
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(request.user.id)}
        ))
    can, msg = instance.can_view(request.user)
    if not can:
        messages.error(request, msg or "Vous ne pouvez pas accéder à ce menu")
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(request.user.id)}
        ))
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    reversions = Version.objects.get_for_object(instance)
    if hasattr(instance, 'linked_objects'):
        for related_object in chain(instance.linked_objects()):
            reversions = (reversions |
                          Version.objects.get_for_object(related_object))
    reversions = re2o_paginator(request, reversions, pagination_number)
    return render(
        request,
        're2o/history.html',
        {'reversions': reversions, 'object': instance}
    )


@cache_page(7 * 24 * 60 * 60)
def about_page(request):
    """ The view for the about page.
    Fetch some info about the configuration of the project. If it can't
    get the info from the Git repository, fallback to default string """
    option = AssoOption.objects.get()
    git_info_contributors = CONTRIBUTORS
    try:
        git_repo = git.Repo(settings.BASE_DIR)
        git_info_remote = ", ".join(git_repo.remote().urls)
        git_info_branch = git_repo.active_branch.name
        last_commit = git_repo.commit()
        git_info_commit = last_commit.hexsha
        git_info_commit_date = last_commit.committed_datetime
    except:
        NO_GIT_MSG = _("Unable to get the information")
        git_info_remote = NO_GIT_MSG
        git_info_branch = NO_GIT_MSG
        git_info_commit = NO_GIT_MSG
        git_info_commit_date = NO_GIT_MSG

    dependencies = settings.INSTALLED_APPS + settings.MIDDLEWARE_CLASSES

    return render(
        request,
        "re2o/about.html",
        {
            'description': option.description,
            'AssoName': option.name,
            'git_info_contributors': git_info_contributors,
            'git_info_remote': git_info_remote,
            'git_info_branch': git_info_branch,
            'git_info_commit': git_info_commit,
            'git_info_commit_date': git_info_commit_date,
            'dependencies': dependencies
        }
    )

def contact_page(request):
    """The view for the contact page
    Send all the objects MailContact
    """
    address = MailContact.objects.all()

    return render(
        request,
        "re2o/contact.html",
        {
            'contacts': address,
            'asso_name': AssoOption.objects.first().name
        }
    )


def handler500(request):
    """The handler view for a 500 error"""
    return render(request, 'errors/500.html')
