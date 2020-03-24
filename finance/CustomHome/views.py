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

@login_required(login_url='CustomHome:login')
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

@login_required(login_url='CustomHome:login')
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

@login_required(login_url='CustomHome:login')
def viewBudgetInfo(request):
    #RAW SQL QUERY TO GET EVERYTHING FROM TABLE CALLED: customhome_budgetinfo
    userName = request.user.get_username()
    print(type(userName))
    #userID = User.objects.raw('SELECT * FROM auth_user WHERE username = %s', [userName])
    #budget = BudgetInfo.objects.raw('SELECT * FROM customhome_budgetinfo WHERE user_id= %s',[userID])

    #USERID is the query set returned from this raw query
    USERID = User.objects.raw('SELECT id FROM auth_user WHERE username = %s LIMIT 1',[userName])

    #Now we have to get the actual ID from the query set returned
    #we first set actualID to be some dummy number that it can't possibly be (-1)
    actualID = -1
    #then, we get the actualID (if applicable) and set it (if applicable)
    for obj in USERID:
        actualID = obj.id

    #BUDGET IS QUERY RESULT
    budget = BudgetInfo.objects.raw('SELECT * FROM customhome_budgetinfo WHERE user_id = %s', [actualID])


    #PUTS QUERY RESULTS INTO A DICTIONARY TO BE PASSED IN AS A CONTEXT
    args = {'budget':budget}
    return render(request, 'CustomHome/viewBudgetInfo.html', args)
