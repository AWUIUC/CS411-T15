from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *

class BudgetAmountForm(forms.Form):
    amount = forms.IntegerField(label='Total amount under per month')

class BudgetPercentageForm(forms.Form):
    groceries = forms.IntegerField(label=category_choices[0][0])
    education = forms.IntegerField(label=category_choices[1][0])
    travel = forms.IntegerField(label=category_choices[2][0])
    rnb = forms.IntegerField(label=category_choices[3][0])
    bnu = forms.IntegerField(label=category_choices[4][0])
    shopping = forms.IntegerField(label=category_choices[5][0])
    entertainment = forms.IntegerField(label=category_choices[6][0])
    gas = forms.IntegerField(label=category_choices[7][0])
    misc = forms.IntegerField(label=category_choices[8][0])

    def clean(self):
        cd = self.cleaned_data
        groceries=cd.get('groceries')
        education=cd.get('education')
        travel=cd.get('travel')
        rnb=cd.get('rnb')
        bnu=cd.get('bnu')
        shopping=cd.get('shopping')
        entertainment=cd.get('entertainment')
        gas=cd.get('gas')
        misc=cd.get('misc')
        if (groceries+education+travel+rnb+bnu+shopping+entertainment+gas+misc) != 100:
            raise forms.ValidationError("Percentages need to add up to 100%")
        return cd


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
        #fields = '__all__'
        fields = ['category', 'percentage', 'total_amount_under_per_month']
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(BudgetInfoForm, self).__init__(*args, **kwargs)
    def save(self, *args, **kwargs):
        self.instance.user = self.user
        form = super(BudgetInfoForm, self).save(*args, **kwargs)
        return form

class UpdateBudgetInfoForm(ModelForm):
    class Meta:
        model = BudgetInfo
        fields = ['category', 'percentage', 'total_amount_under_per_month']

class InsertNonregularTransactionForm(ModelForm):
    class Meta:
        model = NonregularTransaction
        fields = ['category', 'amount', 'merchant', 'name','note','date','in_or_out']
        labels = {
            "in_or_out": "Out?"
        }
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(InsertNonregularTransactionForm, self).__init__(*args, **kwargs)
    def save(self, *args, **kwargs):
        self.instance.user = self.user
        form = super(InsertNonregularTransactionForm, self).save(*args, **kwargs)
        return form

class SearchNonregularTransactionForm(forms.Form):
    category = forms.CharField(label='Category', widget=forms.Select(choices=category_choices))
    min_amount = forms.DecimalField(label='Min Amount')
    max_amount = forms.DecimalField(label='Max Amount')
    max_date = forms.DateField(label='Before this Date')
    min_date = forms.DateField(label='After this Date')

class InsertRegularTransactionForm(ModelForm):
    class Meta:
        model = RegularTransaction
        fields = ['category', 'amount', 'merchant', 'name','note','frequency','start_date','in_or_out']
        labels = {
            "in_or_out": "Out?"
        }
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(InsertRegularTransactionForm, self).__init__(*args, **kwargs)
    def save(self, *args, **kwargs):
        self.instance.user = self.user
        form = super(InsertRegularTransactionForm, self).save(*args, **kwargs)
        return form

class RegularTransactionForm(ModelForm):
    class Meta:
        model = RegularTransaction
        fields = ['category', 'amount', 'merchant', 'name','note','frequency','start_date','in_or_out']
        labels = {
            "in_or_out": "Out?"
        }

class NonregularTransactionForm(ModelForm):
    class Meta:
        model = NonregularTransaction
        fields = ['category', 'amount', 'merchant', 'name','note','date','in_or_out']
        labels = {
            "in_or_out": "Out?"
        }

class ProductForm(forms.Form):
    class Meta:
        model = RegularTransaction
        fields = ['category', 'amount', 'merchant', 'name','note','frequency','start_date','in_or_out']
