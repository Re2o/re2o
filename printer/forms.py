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
        self.fields['printAs'].label = 'Print As'
        self.fields['printAs'].empty_label = 'Print As'
        self.fields['disposition'].label = 'disposition'
        self.fields['color'].label = 'color'
        self.fields['count'].label = 'count'

    class Meta:
        model = JobWithOptions
        fields = [
            'file',
            'printAs',
            'color',
            'disposition',
            'count',
            ]


class PrintForm(FormRevMixin, ModelForm):
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(PrintForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['printAs'].label = 'Print As'
        self.fields['disposition'].label = 'disposition'
        self.fields['color'].label = 'color'
        self.fields['count'].label = 'count'

        self.fields['printAs'].widget.attrs['readonly'] = True
        self.fields['filename'].widget.attrs['readonly'] = True
        self.fields['price'].widget.attrs['readonly'] = True
        self.fields['pages'].widget.attrs['readonly'] = True

    class Meta:
        model = JobWithOptions
        exclude = [
            'user',
            'starttime',
            'endtime',
            'status',
            'file',
            ]
