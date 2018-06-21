"""Payment

Here are defined some views dedicated to cheque payement.
"""

from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _

from cotisations.models import Facture as Invoice

from .models import ChequePayment
from .forms import ChequeForm


@login_required
def cheque(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    payment_method = getattr(invoice.paiement, 'payment_method', None)
    if invoice.valid or not isinstance(payment_method, ChequePayment):
        messages.error(
            request,
            _("You cannot pay this invoice with a cheque.")
        )
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': request.user.pk}
        ))
    form = ChequeForm(request.POST or None)
    if form.is_valid():
        invoice.banque = form.cleaned_data['bank']
        invoice.cheque = form.cleaned_data['number']
        invoice.valid = True
        invoice.save()
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': request.user.pk}
        ))
    return render(
        request,
        'cotisations/payment_form.html',
        {'form': form}
    )
