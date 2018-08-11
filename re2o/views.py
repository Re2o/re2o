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
"""
Fonctions de la page d'accueil et diverses fonctions utiles pour tous
les views
"""

from __future__ import unicode_literals

import git

from django.shortcuts import render
from django.template.context_processors import csrf
from django.conf import settings
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

import subprocess
import ipaddress

from preferences.models import (
    Service,
    MailContact,
    AssoOption,
    HomeOption
)
from machines.models import Nas

from .contributors import CONTRIBUTORS
from re2o.settings import CAPTIVE_IP_RANGE

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
        'twitter_account_name': twitter_account_name,
        'facebook_url': facebook_url,
        'asso_name': asso_name
    }, 're2o/index.html', request)

def get_ip(request):
    """Returns the IP of the request, accounting for the possibility of being
    behind a proxy.
    """
    ip = request.META.get("HTTP_X_FORWARDED_FOR", None)
    if ip:
        # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
        ip = ip.split(", ")[0]
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip

def apply(cmd):
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

def mac_from_ip(ip):
    cmd = ['/usr/sbin/arp','-na',ip]
    p = apply(cmd)
    output, errors = p.communicate()
    if output is not None :
        mac_addr = output.decode().split()[3]
        return str(mac_addr)
    else:
        return None

def portail_login(request):
    """ Check for authentication. If success, register the current machine for the user."""
    login_form = AuthenticationForm(data=request.POST)
    success = False
    if login_form.is_valid():
        remote_ip = get_ip(request)
        if ipaddress.ip_address(remote_ip) in ipaddress.ip_network(CAPTIVE_IP_RANGE):
            mac_addr = mac_from_ip(remote_ip)
            if mac_addr:
                nas_type = Nas.objects.get(name="Switches")
                result, reason = login_form.user_cache.autoregister_machine(mac_addr, nas_type)
                if result:
                    success=True
                else:
                    messages.error(request, "Erreur dans l'enregistrement de la machine : %s" % reason, '') 
            else:
                messages.error(request, "Erreur dans la récupération de la MAC")
        else:
            messages.error(request, "Merci de vous connecter en filaire pour enregistrer une machine")
    return form(
        {
            'loginform': login_form,
            'success' : success
        },
        're2o/portail_login.html',
        request
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


def handler404(request):
    """The handler view for a 404 error"""
    return render(request, 'errors/404.html')
