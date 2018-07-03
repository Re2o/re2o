from django.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l
from django.contrib import messages


from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin


class BalancePayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to pay with a cheque.
    """
    payment = models.OneToOneField(
        Paiement,
        related_name='payment_method',
        editable=False
    )
    minimum_balance = models.DecimalField(
        verbose_name=_l("Minimum balance"),
        help_text=_l("The minimal amount of money allowed for the balance"
                     " at the end of a payment. You can specify negative "
                     "amount."
                     ),
        max_digits=5,
        decimal_places=2,
    )
    maximum_balance = models.DecimalField(
        verbose_name=_l("Maximum balance"),
        help_text=_l("The maximal amount of money allowed for the balance."),
        max_digits=5,
        decimal_places=2,
        default=50
    )

    def end_payment(self, invoice, request):
        user = invoice.user
        total_price = invoice.prix_total()
        if float(user.solde) - float(total_price) < self.minimum_balance:
            invoice.valid = False
            invoice.save()
            messages.error(
                request,
                _("Your balance is too low for this operation.")
            )
            return redirect(reverse(
                'users:profil',
                kwargs={'userid': user.id}
            ))
        return invoice.paiement.end_payment(
            invoice,
            request,
            use_payment_method=False
        )
