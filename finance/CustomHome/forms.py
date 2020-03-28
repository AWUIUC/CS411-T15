from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CustomProfileForm(ModelForm): #added on 3.26.20 by AW
    class Meta:
        model = CustomProfile
        fields=['age']


class BudgetInfoForm(ModelForm):
    class Meta:
        model = BudgetInfo
        fields = '__all__'



class InsertNonregularTransactionForm(ModelForm):
    class Meta:
        model = NonregularTransaction
        fields = ['category', 'amount', 'merchant', 'name','note','date','in_or_out']
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(InsertNonregularTransactionForm, self).__init__(*args, **kwargs)
    def save(self, *args, **kwargs):
        self.instance.user = self.user
        form = super(InsertNonregularTransactionForm, self).save(*args, **kwargs)
        return form

class InsertRegularTransactionForm(ModelForm):
    class Meta:
        model = RegularTransaction
        fields = ['category', 'amount', 'merchant', 'name','note','frequency','start_date','in_or_out']
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(InsertRegularTransactionForm, self).__init__(*args, **kwargs)
    def save(self, *args, **kwargs):
        self.instance.user = self.user
        form = super(InsertRegularTransactionForm, self).save(*args, **kwargs)
        return form
