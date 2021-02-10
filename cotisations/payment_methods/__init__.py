# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Hugo Levy-Falk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
# Custom Payment methods

When creating an invoice with a classic payment method, the creation view calls
the `end_payment` method of the `Payment` object of the invoice. This method
checks for a payment method associated to the `Payment` and if nothing is
found, adds a message for payment confirmation and redirects the user towards
their profil page. This is fine for most of the payment method, but you might
want to define custom payment methods. As an example for negociating with an
other server for online payment or updating some fields in your models.

# Defining a custom payment method
To define a custom payment method, you can add a Python module to
`cotisations/payment_methods/`. This module should be organized like
a Django application.
As an example, if you want to add the payment method `foo`.

## Basic

The first thing to do is to create a `foo` Python module with a `models.py`.

```
payment_methods
├── foo
│   ├── __init__.py
│   └── models.py
├── forms.py
├── __init__.py
├── mixins.py
└── urls.py
```

Then, in `models.py` you could add a model like this :
```python
from django.db import models

from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin


# The `PaymentMethodMixin` defines the default `end_payment`
class FooPayment(PaymentMethodMixin, models.Model):

    # This field is required, it is used by `Paiement` in order to
    # determine if a payment method is associated to it.
    payment = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE,
        related_name='payment_method',
        editable=False
    )
```

And in `__init__.py` :
```python
from . import models
NAME = "FOO" # Name displayed when you crate a payment type
PaymentMethod = models.FooPayment # You must define this alias
```

Then you just have to register your payment method in
`payment_methods/__init__.py` in the `PAYMENT_METHODS` list :

```
from . import ... # Some existing imports
from . import foo

PAYMENT_METHODS = [
    # Some already registered payment methods...
    foo
]
```

And... that's it, you can use your new payment method after running
`makemigrations` and `migrate`.

But this payment method is not really usefull, since it does noting !

## A payment method which does something

You have to redefine the `end_payment` method. Here is its prototype :

```python
def end_payment(self, invoice, request):
    pass
```

With `invoice` the invoice being created and `request` the request which
created it. This method has to return an HttpResponse-like object.

## Additional views

You can add specific urls for your payment method like in any django app. To
register these urls, modify `payment_methods/urls.py`.

## Alter the `Paiement` object after creation

You can do that by adding a `alter_payment(self, payment)`
method to your model.

## Validate the creation field

You may want to perform some additionals verifications on the form
creating the payment. You can do that by adding a `valid_form(self, form)`
method to your model, where `form` is an instance of
`cotisations.payment_methods.forms.PaymentMethodForm`.
"""


from . import balance, cheque, comnpay, free, note_kfet, urls

PAYMENT_METHODS = [comnpay, cheque, balance, note_kfet, free]
