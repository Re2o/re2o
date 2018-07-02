from django import forms
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l

from . import PAYMENT_METHODS
from cotisations.utils import find_payment_method

def payment_method_factory(payment, *args, **kwargs):
    payment_method = kwargs.pop('instance', find_payment_method(payment))
    if payment_method is not None:
        return forms.modelform_factory(type(payment_method), fields='__all__')(
            *args,
            instance=payment_method,
            **kwargs
        )
    return PaymentMethodForm(payment_method, *args, **kwargs)


class PaymentMethodForm(forms.Form):
    """A special form which allows you to add a payment method to a `Payment`
    objects if it hasn't one yet, or to edit the existing payment method.

    To do so it replaces itself with a `modelform_factory`.
    """

    payment_method = forms.ChoiceField(
        label=_l("Special payment method"),
        required=False
    )

    def __init__(self, payment_method, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        if payment_method is None:
            prefix = kwargs.get('prefix', None)
            self.fields['payment_method'].choices = [(i,p.NAME) for (i,p) in enumerate(PAYMENT_METHODS)]
            self.fields['payment_method'].choices.insert(0, ('', _l('no')))
            self.fields['payment_method'].widget.attrs = {
                'id': 'paymentMethodSelect'
            }
            self.templates = [
                forms.modelform_factory(p.PaymentMethod, fields='__all__')(prefix=prefix)
                for p in PAYMENT_METHODS
            ]
        else:
            self.fields = {}

    def save(self, *args, payment=None, **kwargs):
        commit = kwargs.pop('commit', True)
        choice = self.cleaned_data['payment_method']
        if choice=='':
            return
        choice = int(choice)
        model = PAYMENT_METHODS[choice].PaymentMethod
        form = forms.modelform_factory(model, fields='__all__')(self.data, prefix=self.prefix)
        payment_method = form.save(commit=False)
        payment_method.payment = payment
        if commit:
            payment_method.save()
        return payment_method
