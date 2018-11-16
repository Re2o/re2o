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
from django.utils.translation import ugettext as _

from re2o.views import form
from users.models import User
from re2o.base import re2o_paginator
from . import settings

from .utils import pdfinfo, send_mail_printer

from .models import (
    JobWithOptions,
    PrintOperation
    )
from .forms import (
    JobWithOptionsForm,
    PrintAgainForm
    )

from preferences.models import GeneralOption
from cotisations.models import(
    Paiement,
    Facture,
    Vente,
)
from cotisations.utils import find_payment_method
from cotisations.payment_methods.balance.models import BalancePayment

from django.core.exceptions import ValidationError
from re2o.acl import (
    can_edit
)

@login_required
def new_job(request):
    """
    View to create a new printing job
    """
    print_operation = PrintOperation(user=request.user)

    job_formset = formset_factory(JobWithOptionsForm)(
        request.POST or None,
        request.FILES or None,
        form_kwargs={'user': request.user},
    )

    if job_formset.is_valid():
        job_form = job_formset
        print_operation.save()
        for count, job in enumerate(job_form):
            ### Fails if one of the forms is submitted without a file.
            try:
                filename = job.cleaned_data['file'].name
                job_instance = job.save(commit=False)
                job_instance.filename = filename
                job_instance.print_operation = print_operation
                job_instance.user=request.user
                metadata = pdfinfo(request.FILES['form-%s-file' % count].temporary_file_path())
                if "Pages" in metadata:
                    job_instance.pages = metadata["Pages"]
                    job_instance.save()
                else:
                    job_form.erros[count] = {'file': ['Invalid PDF']}
            except KeyError:
                job_form.errors[count] = {'file': ['This field is required.']}
        if job_formset.total_error_count() == 0:
            return redirect(reverse(
                'printer:print-job',
                kwargs={'printoperationid': print_operation.id}
            ))

    return form(
        {
            'jobform': job_formset,
            'action_name': _('Next'),
        },
        'printer/newjob.html',
        request
    )


@login_required
@can_edit(PrintOperation)
def print_job(request, printoperation, **_kwargs):
    """Print a job, confirm after new job step"""
    jobs_to_edit = JobWithOptions.objects.filter(print_operation=printoperation)
    job_modelformset = modelformset_factory(
        JobWithOptions,
        extra=0,
        fields=('color', 'disposition', 'count', 'stapling', 'perforation'),
        max_num=jobs_to_edit.count()
    )
    job_formset = job_modelformset(
        request.POST or None,
        queryset=jobs_to_edit
    )
    if job_formset.is_valid():
        job_formset.save()
        for job_form in job_formset:
            job = job_form.instance
            job.status = 'Printable'
            job.save()
        return payment(request, jobs_to_edit)
    return form(
        {
            'jobform': job_formset,
            'action_name': _('Print'),
        },
        'printer/print.html',
        request
    )

@login_required
@can_edit(JobWithOptions)
def print_job_again(request, jobwithoptions, **_kwargs):
    """Print a job again"""
    jobwithoptionsform = formset_factory(PrintAgainForm)(
        request.POST or None,
        request.FILES or None,
        form_kwargs={'user': request.user, 'instance': jobwithoptions},
    )
    if jobwithoptionsform.is_valid():
        for job_form in jobwithoptionsform:
            jobwithoptions = job_form.instance
            jobwithoptions.pk = None
            jobwithoptions.print_operation = PrintOperation.objects.create(user=jobwithoptions.print_operation.user)
            jobwithoptions.status = 'Running'
            jobwithoptions.save()
            return payment(request, [jobwithoptions])
    return form(
        {
            'jobform': jobwithoptionsform,
            'action_name': _('Print'),
        },
        'printer/print.html',
        request
    ) 


def payment(request, jobs):
    """
    View used to create a new invoice and make the payment
    """
    success = 0
    users = {}
    for job in jobs:
        try:
            users[job.printAs or job.user][0]+=job.price
            users[job.printAs or job.user][1].append(job.id)
        except KeyError:
            users[job.printAs or job.user]=[job.price, [job.id]]

    balancePayment =  BalancePayment.objects.get()
    minimum_balance = balancePayment.minimum_balance
    for user in users:
        ### If payment_method balance doesn't exist, then you're not allowed to print.
        try:
            balance = find_payment_method(Paiement.objects.get(is_balance=True))
        except Paiement.DoesNotExist:
            messages.error(
                request,
                _("You are not allowed to print")
            )
            return redirect(reverse(
                'users:profil',
                kwargs={'userid': request.user.id}
            ))
        invoice = Facture(user=user)
        invoice.paiement = balance.payment
        invoice.save()
        Vente.objects.create(
            facture=invoice,
            name='Impressions',
            prix=users[user][0],
            number=1,
        )
        invoice.paiement.end_payment(invoice, request)
        ### If we are here, then either we were able to pay and it's ok,
        ### Either we weren't able to pay and we need to cancel the jobs.
        jobs = JobWithOptions.objects.filter(id__in=users[user][1])
        if float(user.solde) - float(users[user][0]) < 0:
            for job in jobs:
                job.status = 'Cancelled'
                job.save()
        else:
            for job in jobs:
                job.paid = True
                job.save()
                success=1
    if success:
        send_mail_printer(request.user)
    return redirect(reverse(
        'users:profil',
        kwargs={'userid': str(request.user.id)}
    ))

@login_required
def index_jobs(request):
    """ Display jobs"""
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    jobs = JobWithOptions.objects.select_related('user')\
        .select_related('print_operation')\
        .order_by('starttime').reverse()
    jobs_list = re2o_paginator(request, jobs, pagination_number)
    return render(request, 'printer/index_jobs.html', {'jobs_list': jobs_list})
