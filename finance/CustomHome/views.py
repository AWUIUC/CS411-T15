from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.db import connection

from .models import *
from .forms import *
from django.views.generic.list import ListView

# Create your views here.
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('CustomHome:home')
    else:
        form = CreateUserForm()
        custom_ProfileForm = CustomProfileForm() #added 3.26.20 by AW

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            custom_ProfileForm = CustomProfileForm(request.POST) #added 3.26.20 by AW

            if form.is_valid() and custom_ProfileForm.is_valid(): #changed 3.26.20 by AW
                user = form.save() #changed from form.save() to user = form.save() 3.26.20 by AW

                profile = custom_ProfileForm.save(commit=False) #added 3.26.20 AW we set commit=False so we can create profile object but not save it
                profile.user = user #added by AW 3.26.20
                profile.save() #added by AW 3.26.20

                temp_user = form.cleaned_data.get('username') #changed user to temp_user 3.26.20 by AW
                messages.success(request, 'Account was created for' + temp_user) #changed user to temp_user 3.26.20 by AW

                return redirect('CustomHome:login')

        context = {'form':form, 'custom_ProfileForm':custom_ProfileForm}
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

@login_required(login_url='CustomHome:login')
def createBudget(request):
    form = BudgetInfoForm()
    if request.method == 'POST':
        form = BudgetInfoForm(request.POST)
        if form.is_valid():
            b = form.save(commit=False)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO customhome_budgetinfo VALUES(%s,%s,%s,%s,%s);", [b.id,b.category,b.percentage,b.total_amount_under_per_month,request.user.id])
            return redirect('CustomHome:viewBudgetInfo')

    context = {'form':form}
    return render(request, 'CustomHome/budget_form.html', context)

@login_required(login_url='CustomHome:login')
def updateBudget(request, pk):
    budget = BudgetInfo.objects.get(id=pk)
    form = BudgetInfoForm(instance=budget)

    if request.method == 'POST':
        form = BudgetInfoForm(request.POST, instance=budget) #we cant JUST pass in request.POST because it will create a new item
        if form.is_valid():
            b = form.save(commit=False)
            cursor = connection.cursor()
            cursor.execute("UPDATE customhome_budgetinfo SET id=%s,category=%s,percentage=%s,total_amount_under_per_month=%s,user_id=%s WHERE id=%s;", [b.id,b.category,b.percentage,b.total_amount_under_per_month,request.user.id, pk])
            return redirect('CustomHome:viewBudgetInfo')

    context = {'form':form}
    return render(request, 'CustomHome/budget_form.html', context)

@login_required(login_url='CustomHome:login')
def deleteBudget(request, pk):
    budget = BudgetInfo.objects.get(id=pk)
    if request.method == "POST":
        #budget.delete()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM customhome_budgetinfo WHERE id=%s", [pk])
        return redirect('CustomHome:viewBudgetInfo')
    context = {'item':budget}
    return render(request, 'CustomHome/budget_delete.html', context)
    
@login_required(login_url='CustomHome:login')
def viewRegularTransaction(request):
    #paginate_by = 100  # if pagination is desired
    #userID = User.objects.raw('SELECT * FROM auth_user WHERE username = %s', [userName])
    #budget = BudgetInfo.objects.raw('SELECT * FROM customhome_budgetinfo WHERE user_id= %s',[userID])

    #USERID is the query set returned from this raw query
    USERID = request.user.id
    queryset = RegularTransaction.objects.raw('SELECT * FROM customhome_regulartransaction WHERE user_id = %s',[USERID])
    context = {'regulartransaction_list':queryset, 'userid':USERID}
    return render(request, 'CustomHome/regulartransaction_list.html',context)

@login_required(login_url='CustomHome:login')
def viewNonregularTransaction(request):
    #paginate_by = 100  # if pagination is desired
    userName = request.user.get_username()
    #userID = User.objects.raw('SELECT * FROM auth_user WHERE username = %s', [userName])
    #budget = BudgetInfo.objects.raw('SELECT * FROM customhome_budgetinfo WHERE user_id= %s',[userID])

    #USERID is the query set returned from this raw query
    USERID = request.user.id
    queryset = NonregularTransaction.objects.raw('SELECT * FROM customhome_nonregulartransaction WHERE user_id = %s',[USERID])
    context = {'nonregulartransaction_list':queryset, 'userid':USERID}
    return render(request, 'CustomHome/nonregulartransaction_list.html',context)

@login_required(login_url='CustomHome:login')
def updateRegularTransaction(request, pk):
    obj = RegularTransaction.objects.raw('SELECT * FROM customhome_regulartransaction WHERE id = %s',[pk])[0]
    form = RegularTransactionForm(instance=obj)

    if request.method == 'POST':
        form = RegularTransactionForm(request.POST, instance=obj) #we cant JUST pass in request.POST because it will create a new item
        if form.is_valid():
            t = form.save(commit=False)
            #raw sql insert query
            cursor = connection.cursor()
            cursor.execute("UPDATE customhome_regulartransaction SET id=%s,category=%s,amount=%s,merchant=%s,name=%s,note=%s,frequency=%s,in_or_out=%s,user_id=%s,start_date=%s WHERE id = %s", [t.id,t.category,t.amount,t.merchant,t.name,t.note,t.frequency,t.in_or_out,t.user_id,t.start_date, pk])
            return redirect('CustomHome:viewRegularTransaction')

    context = {'form':form}
    return render(request, 'CustomHome/updateRegularTransaction.html', context)

@login_required(login_url='CustomHome:login')
def deleteRegularTransaction(request, pk):
    obj = RegularTransaction.objects.raw('SELECT * FROM customhome_regulartransaction WHERE id = %s',[pk])[0]
    if request.method == "POST":
        #obj.delete()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM customhome_regulartransaction WHERE id=%s", [pk])
            
        return redirect('CustomHome:viewRegularTransaction')
    context = {'item':obj}
    return render(request, 'CustomHome/deleteRegularTransaction.html', context)

@login_required(login_url='CustomHome:login')
def updateNonregularTransaction(request, pk):
    obj = NonregularTransaction.objects.raw('SELECT * FROM customhome_nonregulartransaction WHERE id = %s',[pk])[0]
    form = NonregularTransactionForm(instance=obj)

    if request.method == 'POST':
        form = NonregularTransactionForm(request.POST, instance=obj) #we cant JUST pass in request.POST because it will create a new item
        if form.is_valid():
            t = form.save(commit=False)
            #raw sql insert query
            cursor = connection.cursor()
            cursor.execute("UPDATE customhome_nonregulartransaction SET id=%s,category=%s,amount=%s,merchant=%s,name=%s,note=%s,in_or_out=%s,user_id=%s,date=%s WHERE id = %s", [t.id,t.category,t.amount,t.merchant,t.name,t.note,t.in_or_out,t.user_id,t.date, pk])
            
            return redirect('CustomHome:viewNonregularTransaction')

    context = {'form':form}
    return render(request, 'CustomHome/updateNonregularTransaction.html', context)

@login_required(login_url='CustomHome:login')
def deleteNonregularTransaction(request, pk):
    obj = NonregularTransaction.objects.raw('SELECT * FROM customhome_nonregulartransaction WHERE id = %s',[pk])[0]
    if request.method == "POST":
        cursor = connection.cursor()
        cursor.execute("DELETE FROM customhome_nonregulartransaction WHERE id=%s", [pk])

        return redirect('CustomHome:viewNonregularTransaction')
    context = {'item':obj}
    return render(request, 'CustomHome/deleteNonregularTransaction.html', context)