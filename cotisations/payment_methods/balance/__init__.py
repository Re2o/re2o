"""
This module contains a method to pay online using user balance.
"""
from . import models
NAME = "BALANCE"

PaymentMethod = models.BalancePayment
