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

from .utils import pdfinfo

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

from django.core.exceptions import ValidationError

@login_required
def new_job(request):
    """
    View to create a new printing job
    """
    if request.method == 'POST':
        # raise Exception('coucou3')
        # raise ValidationError("'%(path)s'", code='path', params = {'path': request.FILES})

        job_formset = formset_factory(JobWithOptionsForm)(
            request.POST,
            request.FILES or None,
            form_kwargs={'user': request.user},
        )

        # raise ValidationError("'%(path)s'", code='path', params = {'path': request.FILES})


        tmp_job_formset = job_formset

        if request.FILES:
            # raise Exception("Coucou4")

            if job_formset.is_valid():
                # raise Exception("Valide !!!")
                files = request.FILES
                data = []
                i=0
                # request.POST['jids'] = []
                jids = []
                for job in job_formset.forms:
                    if job.is_valid():
                        try:
                            filename = job.cleaned_data['file'].name
                        except KeyError:
                            raise ValidationError("'%(path)s'", code='path', params = {'path': job})
                        job = job.save(commit=False)
                        job.filename = filename
                        job.user=request.user
                        # raise ValidationError("'%(path)s'", code='path', params = {'path': job.printAs})
                        if job.printAs is None:
                            job.printAs = request.user
                        job.status='Pending'
                        # raise
                        # raise ValidationError("'%(path)s'", code='path', params = {'path': request.FILES['form-%s-file' % i].temporary_file_path()})
                        # job_data = model_to_dict(job)
                        # raise ValidationError("'%(plop)s'", code='plop', params = {'plop': bool(job.printAs is None) })
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
                        jids.append(job.id)
                        # request.session['id-form-%s-file' % i] = job.id
                        # request.session['form-%s-file' % i] = request.FILES['form-%s-file' % i].temporary_file_path()
                        job_data['jid'] = job.id
                        data.append(job_data)
                        i+=1
                job_formset_filled_in = formset_factory(PrintForm, extra=0)(
                    initial=data,
                    # jids=jids,
                    form_kwargs={'user': request.user,
                    },
                )
                # raise ValidationError("'%(path)s'", code='path', params = {'path': job_formset_filled_in.forms })

                # request.POST['job_ids'] = jids
                return form(
                    {
                        'jobform': job_formset_filled_in,
                        'action_name' : 'Print',
                    },
                    'printer/print.html',
                    request
                )
            else:
                job_formset = tmp_job_formset
                return form(
                    {
                        'jobform': job_formset,
                        'action_name': _("Next"),
                    },
                    'printer/newjob.html',
                    request
                )

        # else:
        #     job_formset = tmp_job_formset
        #     return form(
        #         {
        #             'jobform': job_formset,
        #             'action_name': _("Next"),
        #         },
        #         'printer/newjob.html',
        #         request
        #     )


    # else:
    #     raise Exception("Coucou5")
        # elif 'Print' in request.POST:
        # raise ValidationError("'%(path)s'", code='path', params = {'path': request.POST })

        # raise Exception('On a déjà upload !')
        # n = int(request.POST['form-TOTAL_FORMS'])
        job_formset = formset_factory(PrintForm)(
            request.POST,
            form_kwargs={'user': request.user},
        )
        # raise ValidationError("'%(path)s'", code='path', params = {'path': request.POST })
        # jids = request.POST['job_ids']
        if job_formset.is_valid():
            for job_form in job_formset:
                i=0
                # old_job = JobWithOptions.objects.get(id=jids[i])
                jid = job_form.cleaned_data['jid']
                # raise ValidationError("'%(path)s'", code='path', params = {'path': job_obj.cleaned_data })
                job = JobWithOptions.objects.get(id=jid)
                # job = job_obj.save(commit=False)
                job.user = request.user
                job.status = 'Printable'
                # raise ValidationError("'%(plop)s'", code='plop', params = {'plop': job.file})
                # job.file = old_job.file
                job._update_price()
                job.save()
                i+=1
                # raise ValidationError("'%(plop)s'", code='plop', params = {'plop': request.method})
                # raise ValidationError("'%(path)s'", code='path', params = {'path': str(n) })
            # request.session['jids']=jids
            return redirect('printer:payment')


    else:
        # raise Exception("Coucou2")
        job_formset = formset_factory(JobWithOptionsForm)(
            form_kwargs={'user': request.user}
        )
    # raise ValidationError("'%(plop)s'", code='plop', params = {'plop': job_formset})

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
    # user = request.user
    # jids = request.session['jids']
    # raise ValidationError("'%(path)s'", code='path', params = {'path': jids})
    jobs = JobWithOptions.objects.filter(user=request.user, status='Printable', paid='False')
    users = {}
    for job in jobs:
        try:
            users[job.printAs]+=job.price
            job.paid = True
            job.save()
        except KeyError:
            users[job.printAs]=job.price
            job.paid = True
            job.save()

    for user in users:
        # If payment_method balance doesn't exist, then you're not allowed to print.
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
        # invoice.valid = True
        invoice.save()
        Vente.objects.create(
            facture=invoice,
            name='Printing (requested by %s)' % request.user,
            prix=users[user],
            number=1,
        )
        invoice.paiement.end_payment(invoice, request)
    return redirect(reverse(
        'printer:success',
    ))

def success(request):
    return form(
        {},
        'printer/success.html',
        request
        )
