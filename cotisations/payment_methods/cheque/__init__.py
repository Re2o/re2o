"""
This module contains a method to pay online using cheque.
"""
from . import models, urls, views
NAME = "CHEQUE"

PaymentMethod = models.ChequePayment
