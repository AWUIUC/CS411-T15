from django.db import models
import datetime
from django.conf import settings
from django.utils import timezone

from django.contrib.auth.models import User #added 3.26.20 by AW - extending the existing User Model
from django.core.validators import MaxValueValidator, MinValueValidator #added 3.26.20 by AW - making sure people dont put invalid ages

category_choices = [
    ('Groceries', 'Groceries'),
    ('Education', 'Education'),
    ('Travel', 'Travel'),
    ('Restaurant & Bars', 'Restaurant & Bars'),
    ('Bills & Utilities', 'Bills & Utilities'),
    ('Shopping', 'Shopping'),
    ('Entertainment', 'Entertainment'),
    ('Gas', 'Gas'),
    ('Misc', 'Misc'),
]

category_form_choices = ['groceries','education','travel','rnb','bnu','shopping','entertainment','gas','misc',]

category_default_values = [10,10,10,10,10,10,10,10,20,]

class CustomProfile(models.Model): #added 3.26.20 by AW - extending the existing User Model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(
        validators = [MinValueValidator(0), MaxValueValidator(200)]
    ) #age can not be less than 0 or greater than 200

    def __str__(self):
        return self.user.username


class BudgetInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category=models.CharField(max_length=255, choices=category_choices)
    percentage=models.IntegerField()
    total_amount_under_per_month=models.IntegerField()
    def __str__(self):
        return self.category

class RegularTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category=models.CharField(max_length=255, choices=category_choices)
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
    category=models.CharField(max_length=255, choices=category_choices)
    amount=models.DecimalField(max_digits=19, decimal_places=2)
    merchant=models.CharField(max_length=255)
    name=models.CharField(max_length=255)
    note=models.CharField(max_length=255)
    date=models.DateField()
    in_or_out=models.BooleanField()
