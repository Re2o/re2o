from django.forms import ValidationError
from django.utils.translation import ugettext as _


def check_no_balance(is_balance):
    """This functions checks that no Paiement with is_balance=True exists

    Args:
        is_balance: True if the model is balance.

    Raises:
        ValidationError: if such a Paiement exists.
    """
    from .models import Paiement
    if not is_balance:
        return
    p = Paiement.objects.filter(is_balance=True)
    if len(p) > 0:
        raise ValidationError(
            _("There is already a payment method for user balance.")
        )

