# -*- mode: python; coding: utf-8 -*-

"""printer.forms
Form to add, edit, cancel printer jobs.
Author : Maxime Bombar <bombar@crans.org>.
Date : 29/06/2018
"""

from django import forms
from django.forms import (
    Form,
    ModelForm,
)

import itertools

from re2o.mixins import FormRevMixin

from .models import (
    JobWithOptions,
)


class JobWithOptionsForm(FormRevMixin, ModelForm):
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(JobWithOptionsForm, self).__init__(*args, prefix=prefix, **kwargs)

    class Meta:
        model = JobWithOptions
        fields = [
            'file',
            'color',
            'disposition',
            'count',
            ]
                
