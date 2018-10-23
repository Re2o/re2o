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

from . import settings

from .utils import pdfinfo, send_mail_printer

from .models import (
    JobWithOptions,
    )

from .forms import (
    JobWithOptionsForm,
    PrintForm,
    )


from cotisations.models import(
    Paiement,
    Facture,
    Vente,
)

from cotisations.utils import find_payment_method

from cotisations.payment_methods.balance.models import BalancePayment

from django.core.exceptions import ValidationError

# raise ValidationError("'%(path)s'", code='path', params = {'path': job.printAs})

@login_required
def new_job(request):
    """
    View to create a new printing job
    """
    if request.method == 'POST':

        ### First Step
        if 'Next' in request.POST:
            job_formset = formset_factory(JobWithOptionsForm)(
                request.POST,
                request.FILES or None,
                form_kwargs={'user': request.user},
            )



            if job_formset.is_valid():
                data = []
                i=0
                for job in job_formset:
                    ### Fails if one of the forms is submitted without a file.
                    try:
                        filename = job.cleaned_data['file'].name
                        job = job.save(commit=False)
                        job.filename = filename
                        job.user=request.user
                        if job.printAs is None:
                            job.printAs = request.user
                        job.status='Pending'
                        metadata = pdfinfo(request.FILES['form-%s-file' % i].temporary_file_path())
                        job.pages = metadata["Pages"]
                        job._update_price()
                        job.save()
                        job_data = model_to_dict(job)
                        job_data['jid'] = job.id
                        data.append(job_data)
                    except KeyError:
                        job_formset.errors[i] = {'file': ['This field is required.']}
                    i+=1
                job_formset_filled_in = formset_factory(PrintForm, extra=0)(
                    initial=data,
                    form_kwargs={'user': request.user},
                )

                if job_formset.total_error_count() == 0:
                    ### Every job in the formset has been treated;
                    ### And no empty file. --> Go to next step.
                    return form(
                        {
                            'jobform': job_formset_filled_in,
                            'action_name' : 'Print',
                        },
                        'printer/print.html',
                        request
                    )
                else:
                    ### No file
                    return form(
                        {
                            'jobform': job_formset,
                            'action_name': _("Next"),
                        },
                        'printer/newjob.html',
                        request
                    )

            ### Formset is not valid --> Return the formset with errors
            else:
                return form(
                    {
                        'jobform': job_formset,
                        'action_name': _("Next"),
                    },
                    'printer/newjob.html',
                    request
                )

        ### Second step
        elif 'Print' in request.POST:
            job_formset = formset_factory(PrintForm)(
                request.POST,
                form_kwargs={'user': request.user},
            )
            if job_formset.is_valid():
                for job_form in job_formset:
                    data = job_form.cleaned_data
                    jid = data['jid']
                    job = JobWithOptions.objects.get(id=jid)
                    job.user = request.user
                    job.status = 'Printable'
                    if data['printAs']:
                        job.printAs = data['printAs']
                    job.format = data['format']
                    job.color = data['color']
                    job.disposition = data['disposition']
                    job.count = data['count']
                    job.stapling = data['stapling']
                    job.perforation = data['perforation']
                    job._update_price()
                    job.save()
                return redirect('printer:payment')


    ### GET request
    else:
        job_formset = formset_factory(JobWithOptionsForm)(
            form_kwargs={'user': request.user}
        )


    return form(
        {
            'jobform': job_formset,
            'action_name': _("Next"),
        },
        'printer/newjob.html',
        request
    )

def payment(request):
    """
    View used to create a new invoice and make the payment
    """
    jobs = JobWithOptions.objects.filter(user=request.user, status='Printable', paid='False')
    users = {}
    for job in jobs:
        try:
            users[job.printAs][0]+=job.price
            users[job.printAs][1].append(job.id)
        except KeyError:
            users[job.printAs]=[job.price, [job.id]]

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
            name='Printing (requested by %s)' % request.user,
            prix=users[user][0],
            number=1,
        )
        invoice.paiement.end_payment(invoice, request)
        ### If we are here, then either we were able to pay and it's ok,
        ### Either we weren't able to pay and we need to cancel the jobs.
        jobs = JobWithOptions.objects.filter(id__in=users[user][1])
        if user.solde - users[user][0] < 0:
            for job in jobs:
                job.status = 'Cancelled'
                job.save()
        else:
            for job in jobs:
                job.paid = True
                job.save()

    return redirect(reverse(
        'printer:success',
    ))

def success(request):
    send_mail_printer(request.user)
    return form(
        {},
        'printer/success.html',
        request
        )
