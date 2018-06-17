"""Payment

Here are defined some views dedicated to online payement.
"""

from collections import OrderedDict

from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseBadRequest

from preferences.models import AssoOption
from .models import Facture
from .payment_utils.comnpay import Payment as ComnpayPayment


@csrf_exempt
@login_required
def accept_payment(request, factureid):
    """
    The view called when an online payment has been accepted.
    """
    facture = get_object_or_404(Facture, id=factureid)
    messages.success(
        request,
        _("The payment of %(amount)s € has been accepted.") % {
            'amount': facture.prix()
        }
    )
    return redirect(reverse(
        'users:profil',
        kwargs={'userid': request.user.id}
    ))


@csrf_exempt
@login_required
def refuse_payment(request):
    """
    The view called when an online payment has been refused.
    """
    messages.error(
        request,
        _("The payment has been refused.")
    )
    return redirect(reverse(
        'users:profil',
        kwargs={'userid': request.user.id}
    ))


@csrf_exempt
def ipn(request):
    """
    The view called by Comnpay server to validate the transaction.
    Verify that we can firmly save the user's action and notify
    Comnpay with 400 response if not or with a 200 response if yes
    """
    p = ComnpayPayment()
    order = ('idTpe', 'idTransaction', 'montant', 'result', 'sec', )
    try:
        data = OrderedDict([(f, request.POST[f]) for f in order])
    except MultiValueDictKeyError:
        return HttpResponseBadRequest("HTTP/1.1 400 Bad Request")

    if not p.validSec(data, AssoOption.get_cached_value('payment_pass')):
        return HttpResponseBadRequest("HTTP/1.1 400 Bad Request")

    result = True if (request.POST['result'] == 'OK') else False
    idTpe = request.POST['idTpe']
    idTransaction = request.POST['idTransaction']

    # Checking that the payment is actually for us.
    if not idTpe == AssoOption.get_cached_value('payment_id'):
        return HttpResponseBadRequest("HTTP/1.1 400 Bad Request")

    try:
        factureid = int(idTransaction)
    except ValueError:
        return HttpResponseBadRequest("HTTP/1.1 400 Bad Request")

    facture = get_object_or_404(Facture, id=factureid)

    # Checking that the payment is valid
    if not result:
        # Payment failed: Cancelling the invoice operation
        facture.delete()
        # And send the response to Comnpay indicating we have well
        # received the failure information.
        return HttpResponse("HTTP/1.1 200 OK")

    facture.valid = True
    facture.save()

    # Everything worked we send a reponse to Comnpay indicating that
    # it's ok for them to proceed
    return HttpResponse("HTTP/1.0 200 OK")


def comnpay(facture, request):
    """
    Build a request to start the negociation with Comnpay by using
    a facture id, the price and the secret transaction data stored in
    the preferences.
    """
    host = request.get_host()
    p = ComnpayPayment(
        str(AssoOption.get_cached_value('payment_id')),
        str(AssoOption.get_cached_value('payment_pass')),
        'https://' + host + reverse(
            'cotisations:accept_payment',
            kwargs={'factureid': facture.id}
        ),
        'https://' + host + reverse('cotisations:refuse_payment'),
        'https://' + host + reverse('cotisations:ipn'),
        "",
        "D"
    )
    r = {
        'action': 'https://secure.homologation.comnpay.com',
        'method': 'POST',
        'content': p.buildSecretHTML(
            "Rechargement du solde",
            facture.prix(),
            idTransaction=str(facture.id)
        ),
        'amount': facture.prix(),
    }
    return r


# The payment systems supported by re2o
PAYMENT_SYSTEM = {
    'COMNPAY': comnpay,
    'NONE': None
}
