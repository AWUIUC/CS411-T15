from django.db import models
import datetime
from django.conf import settings
from django.utils import timezone

class BudgetInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category=models.CharField(max_length=255)
    percentage=models.IntegerField()
    total_amount_under_per_month=models.IntegerField()

class RegularTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category=models.CharField(max_length=255)
    amount=models.DecimalField(max_digits=19, decimal_places=2)
    merchant=models.CharField(max_length=255)
    name=models.CharField(max_length=255)
    note=models.CharField(max_length=255)
    #frequency is actually number of days of one cycle, otherwise idk how to store it
    frequency=models.IntegerField()
    in_or_out=models.BooleanField()
    start_date=models.DateField()

class NonregularTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category=models.CharField(max_length=255)
    amount=models.DecimalField(max_digits=19, decimal_places=2)
    merchant=models.CharField(max_length=255)
    name=models.CharField(max_length=255)
    note=models.CharField(max_length=255)
    date=models.DateField()
    in_or_out=models.BooleanField()
