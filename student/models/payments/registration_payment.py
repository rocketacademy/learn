from django.db import models
from payment import Payment


class RegistrationPayment(Payment):
    payable_id = models.CharField(max_length=255)
