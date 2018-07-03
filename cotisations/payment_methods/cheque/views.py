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
from .forms import InvoiceForm


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
    form = InvoiceForm(request.POST or None, instance=invoice)
    if form.is_valid():
        form.instance.valid = True
        form.save()
        return form.instance.paiement.end_payment(
            form.instance,
            request,
            use_payment_method=False
        )
    return render(
        request,
        'cotisations/payment.html',
        {
            'form': form,
            'amount': invoice.prix_total()
        }
    )
