"""
This module contains a method to pay online using comnpay.
"""
from . import models, urls, views
NAME = "COMNPAY"
PaymentMethod = models.ComnpayPayment
