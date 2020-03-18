from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.db import connection

from .models import *
from .forms import *

# Create your views here.
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('CustomHome:home')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for' + user)
                return redirect('CustomHome:login')

        context = {'form':form}
        return render(request, 'CustomHome/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('CustomHome:insertNonregularTransaction')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password = password)

            if user is not None:
                login(request, user)
                return redirect('CustomHome:home')
            else:
                messages.info(request, 'Your username and/or your password is incorrect. Please try again.')
        context = {}
        return render(request, 'CustomHome/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('CustomHome:login')

def insertNonregularTransaction(request):
    if not request.user.is_authenticated:
        return redirect('CustomHome:login')
    else:
        form = InsertNonregularTransactionForm(user=request.user)

        if request.method == 'POST':
            form = InsertNonregularTransactionForm(request.POST,user=request.user)
            if form.is_valid():
                t = form.save(commit=False)
                #raw sql insert query
                cursor = connection.cursor()
                cursor.execute("INSERT INTO customhome_nonregulartransaction VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);", [t.id,t.category,t.amount,t.merchant,t.name,t.note,t.date,t.in_or_out,request.user.id])
                return redirect('CustomHome:home')

        context = {'form':form}
        return render(request, 'CustomHome/insertNonregularTransaction.html', context)

def insertRegularTransaction(request):
    if not request.user.is_authenticated:
        return redirect('CustomHome:login')
    else:
        form = InsertRegularTransactionForm(user=request.user)

        if request.method == 'POST':
            form = InsertRegularTransactionForm(request.POST,user=request.user)
            if form.is_valid():
                t = form.save(commit=False)
                #raw sql insert query
                cursor = connection.cursor()
                cursor.execute("INSERT INTO customhome_regulartransaction VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", [t.id,t.category,t.amount,t.merchant,t.name,t.note,t.frequency,t.in_or_out,request.user.id,t.start_date])
                return redirect('CustomHome:home')

        context = {'form':form}
        return render(request, 'CustomHome/insertRegularTransaction.html', context)


@login_required(login_url='CustomHome:login')
def homePage(request):
    return render(request, 'CustomHome/homePage.html')
