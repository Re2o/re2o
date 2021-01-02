# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2021  Gabriel Détraz
# Copyright © 2021  Jean-Romain Garnier 
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
Re2o Forms and ModelForms Widgets.

Used in others forms for using autocomplete engine.
"""

from django.utils.translation import ugettext as _
from dal import autocomplete


class AutocompleteModelWidget(autocomplete.ModelSelect2):
    """ A mixin subclassing django-autocomplete-light's Select2 model to pass default options
    See https://django-autocomplete-light.readthedocs.io/en/master/tutorial.html#passing-options-to-select2
    """

    def __init__(self, *args, **kwargs):
        select2_attrs = kwargs.get("attrs", {})
        kwargs["attrs"] = self.fill_default_select2_attrs(select2_attrs)

        super().__init__(*args, **kwargs)

    def fill_default_select2_attrs(self, attrs):
        """
        See https://select2.org/configuration/options-api
        """
        # Display the "x" button to clear the input by default
        attrs["data-allow-clear"] = attrs.get("data-allow-clear", "true")
        # If there are less than 10 results, just show all of them (no need to autocomplete)
        attrs["data-minimum-results-for-search"] = attrs.get(
            "data-minimum-results-for-search", 10
        )
        return attrs


class AutocompleteMultipleModelWidget(autocomplete.ModelSelect2Multiple):
    """ A mixin subclassing django-autocomplete-light's Select2 model to pass default options
    See https://django-autocomplete-light.readthedocs.io/en/master/tutorial.html#passing-options-to-select2
    """

    def __init__(self, *args, **kwargs):
        select2_attrs = kwargs.get("attrs", {})
        kwargs["attrs"] = self.fill_default_select2_attrs(select2_attrs)

        super().__init__(*args, **kwargs)

    def fill_default_select2_attrs(self, attrs):
        """
        See https://select2.org/configuration/options-api
        """
        # Display the "x" button to clear the input by default
        attrs["data-allow-clear"] = attrs.get("data-allow-clear", "true")
        # If there are less than 10 results, just show all of them (no need to autocomplete)
        attrs["data-minimum-results-for-search"] = attrs.get(
            "data-minimum-results-for-search", 10
        )
        return attrs
