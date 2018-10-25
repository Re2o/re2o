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

from re2o.mixins import FormRevMixin

from users.models import User

from .models import (
    JobWithOptions,
)


class JobWithOptionsForm(FormRevMixin, ModelForm):
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        self.user = kwargs.pop('user')
        super(JobWithOptionsForm, self).__init__(*args, prefix=prefix, **kwargs)
        if not self.user.adherent.club_members.all():
            self.fields.pop('printAs')
        else:
            self.fields['printAs'].label = _('Print As')
            self.fields['printAs'].empty_label = self.user.pseudo
            self.fields['printAs'].queryset = self.user.adherent.club_members.all()

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


