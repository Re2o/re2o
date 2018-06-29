# -*- mode: python; coding: utf-8 -*-

"""printer.views
The views for the printer app
Author : Maxime Bombar <bombar@crans.org>.
Date : 29/06/2018
"""

from __future__ import unicode_literals

from django.urls import reverse
from django.shortcuts import render, redirect
from django.forms import modelformset_factory, formset_factory

from re2o.views import form
from users.models import User

from . import settings

from .forms import (
    JobWithOptionsForm,
    )


def new_job(request):
    """
    View to create a new printing job
    """
    job_formset = formset_factory(JobWithOptionsForm)(
            request.POST or None, request.FILES or None,
    )
    if job_formset.is_valid():
        for job in job_formset:
            job = job.save(commit=False)
            job.user=request.user
            job.status='Printable'
            job.save()
            return redirect(reverse(
                'printer:success',
            ))
    return form(
        {
            'jobform': job_formset,
            'action_name': "Print",
        },
        'printer/newjob.html',
        request
    )

def success(request):
    return form(
        {},
        'printer/success.html',
        request
        )
