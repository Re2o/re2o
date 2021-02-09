# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
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
Welcom main page view, and several template widely used in re2o views
"""

from __future__ import unicode_literals

import git

from django.shortcuts import render
from django.template.context_processors import csrf
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from dal import autocomplete

from preferences.models import (
    Service,
    MailContact,
    AssoOption,
    HomeOption,
    GeneralOption,
    Mandate,
)

from .contributors import CONTRIBUTORS
from importlib import import_module
from re2o.settings_local import OPTIONNAL_APPS_RE2O


def form(ctx, template, request):
    """Global template function, used in all re2o views, for building a render with context,
    template and request. Adding csrf.
 
    Parameters:
        ctx (dict): Dict of values to transfer to template
        template (django template): The django template of this view
        request (django request)

    Returns:
        Django render: Django render complete view with template, context and request
    """
    context = ctx
    context.update(csrf(request))
    return render(request, template, context)


def index(request):
    """Display all services provided on main page

        Returns: a form with all services linked and description, and social media
        link if provided.

    """
    services = [[], [], []]
    for indice, serv in enumerate(Service.objects.all()):
        services[indice % 3].append(serv)
    twitter_url = HomeOption.get_cached_value("twitter_url")
    facebook_url = HomeOption.get_cached_value("facebook_url")
    twitter_account_name = HomeOption.get_cached_value("twitter_account_name")
    asso_name = AssoOption.get_cached_value("pseudo")
    return form(
        {
            "services_urls": services,
            "twitter_url": twitter_url,
            "twitter_account_name": twitter_account_name,
            "facebook_url": facebook_url,
            "asso_name": asso_name,
        },
        "re2o/index.html",
        request,
    )


def about_page(request):
    """ The view for the about page.
    Fetch some info about the configuration of the project. If it can't
    get the info from the Git repository, fallback to default string """
    option = AssoOption.objects.get()
    general = GeneralOption.objects.get()
    git_info_contributors = CONTRIBUTORS
    try:
        git_repo = git.Repo(settings.BASE_DIR)
        git_info_remote = ", ".join(git_repo.remote().urls)
        git_info_branch = git_repo.active_branch.name
        last_commit = git_repo.commit()
        git_info_commit = last_commit.hexsha
        git_info_commit_date = last_commit.committed_datetime
    except:
        NO_GIT_MSG = _("Unable to get the information.")
        git_info_remote = NO_GIT_MSG
        git_info_branch = NO_GIT_MSG
        git_info_commit = NO_GIT_MSG
        git_info_commit_date = NO_GIT_MSG

    dependencies = settings.INSTALLED_APPS + settings.MIDDLEWARE_CLASSES

    try:
        president = Mandate.get_mandate().president.get_full_name()
    except Mandate.DoesNotExist:
        president = _("Unable to get the information.")

    return render(
        request,
        "re2o/about.html",
        {
            "option": option,
            "gtu": general.GTU,
            "president": president,
            "git_info_contributors": git_info_contributors,
            "git_info_remote": git_info_remote,
            "git_info_branch": git_info_branch,
            "git_info_commit": git_info_commit,
            "git_info_commit_date": git_info_commit_date,
            "dependencies": dependencies,
        },
    )


def contact_page(request):
    """The view for the contact page
    Send all the objects MailContact
    """
    address = MailContact.objects.all()

    optionnal_apps = [import_module(app) for app in OPTIONNAL_APPS_RE2O]
    optionnal_templates_contact_list = [
        app.views.contact(request)
        for app in optionnal_apps
        if hasattr(app.views, "contact")
    ]

    return render(
        request,
        "re2o/contact.html",
        {
            "contacts": address,
            "asso_name": AssoOption.objects.first().name,
            "optionnal_templates_contact_list": optionnal_templates_contact_list,
        },
    )


def handler500(request):
    """The handler view for a 500 error"""
    return render(request, "errors/500.html", status=500)


def handler404(request, exception):
    """The handler view for a 404 error"""
    return render(request, "errors/404.html", status=404)


class AutocompleteLoggedOutViewMixin(autocomplete.Select2QuerySetView):
    obj_type = None  # This MUST be overridden by child class
    query_set = None
    query_filter = "name__icontains"  # Override this if necessary

    def get_queryset(self):
        can, reason, _permission, query_set = self.obj_type.can_list(self.request.user)

        if query_set:
            self.query_set = query_set
        else:
            self.query_set = self.obj_type.objects.none()

        if hasattr(self, "filter_results"):
            self.filter_results()
        else:
            if self.q:
                self.query_set = self.query_set.filter(**{self.query_filter: self.q})

        return self.query_set


class AutocompleteViewMixin(LoginRequiredMixin, AutocompleteLoggedOutViewMixin):
    pass

