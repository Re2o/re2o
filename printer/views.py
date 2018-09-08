# -*- mode: python; coding: utf-8 -*-
"""printer.views
The views for the printer app
Author : Maxime Bombar <bombar@crans.org>.
"""

from __future__ import unicode_literals

from django.urls import reverse
from django.shortcuts import render, redirect
from django.forms import modelformset_factory, formset_factory
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required

from re2o.views import form
from users.models import User

from . import settings

from .utils import pdfinfo

from .models import (
    JobWithOptions,
    )

from .forms import (
    JobWithOptionsForm,
    PrintForm,
    )

from django.core.exceptions import ValidationError

@login_required
def new_job(request):
    """
    View to create a new printing job
    """
    if request.method == 'POST':
        if request.FILES:
            job_formset = formset_factory(JobWithOptionsForm)(
                request.POST,
                request.FILES,
            )

            if job_formset.is_valid():
                files = request.FILES
                data = []
                i=0
                for job in job_formset:
                    # raise ValidationError("'%(path)s'", code='path', params = {'path': job.cleaned_data["file"].name})
                    filename = job.cleaned_data['file'].name
                    job = job.save(commit=False)
                    job.filename = filename
                    job.user=request.user
                    if job.printAs is None:
                        job.printAs = request.user
                    job.status='Printable'
                    # raise
                    # raise ValidationError("'%(path)s'", code='path', params = {'path': request.FILES['form-%s-file' % i].temporary_file_path()})
                    metadata = pdfinfo(request.FILES['form-%s-file' % i].temporary_file_path())
                    job.pages = metadata["Pages"]
                    # raise ValidationError("'%(path)s'", code='path', params = {'path': type(job)})
                    # job.save()
                    # job_data = model_to_dict(job)
                    # job_data['file'] = request.FILES['form-%s-file' % i]
                    # raise ValidationError("'%(plop)s'", code='plop', params = {'plop': job_data })
                    # raise ValidationError("'%(path)s'", code='path', params = {'path': request.session })
                    job._update_price()
                    job.save()
                    job_data = model_to_dict(job)
                    request.session['id-form-%s-file' % i] = job.id
                    request.session['form-%s-file' % i] = request.FILES['form-%s-file' % i].temporary_file_path()
                    # raise ValidationError("'%(plop)s'", code='plop', params = {'plop': job_data })
                    data.append(job_data)
                    i+=1
                job_formset_filled_in = formset_factory(PrintForm, extra=0)(initial=data)
                return form(
                    {
                        'jobform': job_formset_filled_in,
                        'action_name' : 'Print',
                    },
                    'printer/print.html',
                    request
                )

        # elif 'Print' in request.POST:
        # raise ValidationError("'%(path)s'", code='path', params = {'path': request.POST })

        # raise Exception('On a déjà upload !')
        n = int(request.POST['form-TOTAL_FORMS'])
        job_formset = formset_factory(PrintForm)(
            request.POST,
        )
        id_list = [request.session['id-form-%s-file' % i] for i in range(n)]
        # raise ValidationError("'%(path)s'", code='path', params = {'path': id_list })
        if job_formset.is_valid():
            for job_obj in job_formset:
                i=0
                old_job = JobWithOptions.objects.get(id=id_list[i])
                job = job_obj.save(commit=False)
                job.user = request.user
                job.status = 'Running'
                job.file = old_job.file
                job._update_price()
                job.save()
                i+=1
                # raise ValidationError("'%(plop)s'", code='plop', params = {'plop': request.method})
                # raise ValidationError("'%(path)s'", code='path', params = {'path': str(n) })
                return redirect(reverse(
                    'printer:success',
                ))
        raise Exception("Invalid Job_formset")

    else:
        job_formset = formset_factory(JobWithOptionsForm)(
            None,
            )
    return form(
        {
            'jobform': job_formset,
            'action_name': "Advanced Options",
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
