# -*- mode: python; coding: utf-8 -*-

"""printer.forms
Form to add, edit, cancel printer jobs.
Author : Maxime Bombar <bombar@crans.org>.
"""

from django import forms
from django.forms import (
    Form,
    ModelForm,
)
from django.utils.translation import ugettext_lazy as _

import itertools

from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import FormRevMixin

from users.models import User

from .models import (
    JobWithOptions,
)


class JobWithOptionsForm(FieldPermissionFormMixin, FormRevMixin, ModelForm):
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        user=kwargs.get('user')
        super(JobWithOptionsForm, self).__init__(*args, prefix=prefix, **kwargs)
        if 'printAs' in self.fields:
            self.fields['printAs'].label = _('Print As')
            self.fields['printAs'].empty_label = user.pseudo
            self.fields['printAs'].queryset = user.adherent.club_members.all()

    class Meta:
        model = JobWithOptions
        fields = [
            'file',
            'printAs',
            'color',
            'disposition',
            'format',
            'count',
            ]


class PrintAgainForm(JobWithOptionsForm):
    def __init__(self, *args, **kwargs):
        user=kwargs.get('user')
        super(PrintAgainForm, self).__init__(*args, **kwargs)
        if 'printAs' in self.fields:
            self.fields['printAs'].empty_label = user.pseudo
            if self.instance.user != user:
                self.fields['printAs'].queryset = User.objects.filter(club__in=user.adherent.club_members.all()) | User.objects.filter(id=self.instance.user.id)
            else:
                self.fields['printAs'].queryset = user.adherent.club_members.all()

    class Meta:
        model = JobWithOptions
        fields = [
            'printAs',
            'color',
            'disposition',
            'format',
            'count',
            ] 
