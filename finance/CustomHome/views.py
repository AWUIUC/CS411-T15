from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
import sys

from django.contrib.auth import authenticate, login, logout
import json
import decimal
from array import *


from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Scatter
from plotly.graph_objs import Bar
import plotly.graph_objs as go
import  plotly.plotly  as py

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db import connections #ADDED BY AW ON 4.4.20 NOT SAME AS CONNECTION LIBRARY ABOVE
                                  #connections (not connection) allows you to use more than 1 database

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
                messages.success(request, 'Account was created for ' + temp_user) #changed user to temp_user 3.26.20 by AW

                for i in range(9):
                    bi = BudgetInfo()
                    bi.category=category_choices[i][0]
                    bi.percentage=category_default_values[i]
                    bi.total_amount_under_per_month=2000
                    bi.user=user
                    bi.save()
                    
                return redirect('CustomHome:login')

        context = {'form':form, 'custom_ProfileForm':custom_ProfileForm}
        return render(request, 'CustomHome/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('CustomHome:home')
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


    ########################## CODE FOR MONGODB
    import pymongo
    from pymongo import MongoClient
    cluster = MongoClient("mongodb+srv://mongoUser:mongoPass411@cs411-mongo-m207d.mongodb.net/test?retryWrites=true&w=majority")
    db = cluster["data"]
    collection = db["dataCollection"]
    results = collection.find({"name":"bill"})

    ####################### CODE FOR QUERIES WITHIN MYSQL DATABASE
    #cursor = connection.cursor()
    cursor = connections['default'].cursor()
    cursor.execute("SELECT t.user_id AS name, SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id FROM customhome_regulartransaction r UNION ALL SELECT amount, user_id FROM customhome_nonregulartransaction nr WHERE month(nr.date) = 3) t GROUP BY t.user_id")
    resultsFromHomeCursor = cursor.fetchall()
    x_data = [item[0] for item in resultsFromHomeCursor]
    y_data = [item[1] for item in resultsFromHomeCursor]

    # ### Graph for above query
    # trace = go.Pie(labels=x_data,
    #            values=y_data,
    #            textposition='inside',
    #           rotation=90)
    #
    # layout = go.Layout(
    #                 font=dict(family='Arial', size=12, color='#909090'),
    #                 paper_bgcolor='rgba(0,0,0,0)',
    #                 plot_bgcolor='rgba(0,0,0,0)', showlegend=False
    #                 )
    # data = [trace]
    # fig = go.Figure(data=data, layout=layout)
    # plot_div = plot(fig, output_type='div')

    ###################################################### START MYSQL QUERY 1 TO GET TOTAL AMOUNT SPENT LAST MONTH FOR THIS USER ONLY ##############################################
    varA = 35; # DO NOT CHANGE
    varB = 6; # DO NOT CHANGE

    # cursor.execute("DROP TABLE tempX");
    # cursor.execute("DROP TABLE tempY");

    cursor.execute("CREATE TABLE tempX(amount DECIMAL(%s, %s), user_id int)", [varA, varB]);
    cursor.execute("CREATE TABLE tempY(amount DECIMAL(%s, %s), user_id int)", [varA, varB]);

    cursor.execute("INSERT INTO tempX(amount, user_id) SELECT (frequency/12)*amount AS amount, user_id FROM customhome_regulartransaction r WHERE r.start_date <= '2021-05-02'");
    cursor.execute("INSERT INTO tempY(amount, user_id) SELECT amount, user_id FROM customhome_nonregulartransaction WHERE month(date) = '5' AND year(date) = '2021'");

    #cursor.execute("SELECT t.user_id, SUM(t.amount) as total_amount FROM (SELECT * FROM tempX UNION ALL SELECT * FROM tempY) t GROUP BY t.user_id");
    varA = 1 #PUT USER ID INSTEAD OF 1 HERE
    cursor.execute("SELECT SUM(t.amount) as total_amount FROM (SELECT * FROM tempX UNION ALL SELECT * FROM tempY) t WHERE t.user_id=%s", [1])

    totalAmountSpentLastMonth = cursor.fetchall()
    arr = [item[0] for item in totalAmountSpentLastMonth]
    totalAmountSpentLastMonth = float(arr[0])
    totalAmountSpentLastMonth = round(totalAmountSpentLastMonth, 2)

    cursor.execute("DROP TABLE tempX");
    cursor.execute("DROP TABLE tempY");

    ############################################# END MYSQL QUERY 1 ###############################################################################################################


    ######################################### START OF MYSQL QUERY 2 ##############################################################################################################
    varA = 1 #user id
    varB = 1 #month
    varC = 2021 #year
    cursor.execute("SELECT b.category, IFNULL(a.total_amount, 0) as total_amount, b.budget FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-00' AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND nr.user_id = %s) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category", [varA, varB, varC, varA, varA])

    amountPerCategoryForMonth = cursor.fetchall()
    categories = [item[0] for item in amountPerCategoryForMonth]
    spending = [item[1] for item in amountPerCategoryForMonth]
    budget = [item[2] for item in amountPerCategoryForMonth]

    fig = go.Figure(data=[
        go.Bar(name='Spending', x=categories, y=spending),
        go.Bar(name='Budget', x=categories, y=budget)
    ])
    # Change the bar mode
    fig.layout.update(title="Your spending",
    yaxis_title="Amount (in $)", barmode='group', paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)', legend=dict(x=-.1, y=1.2), width=570,
    height=500, font=dict(family="Calibri", size=16, color="#ffffff"))

    current_user_spending_graph = plot(fig, output_type='div')

    labels = categories
    values = budget

    # Use `hole` to create a donut-like pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4)])

    fig.layout.update(title="Budget Categories for Current Month",
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', width=570,
    height=500, font=dict(family="Calibri", size=16, color="#ffffff"))

    budget_pie = plot(fig, output_type='div')

    ##################################### END OF MYSQL QUERY 2 ###################################################################################################################################

    ################################# START OF MYSQL QUERY 3 TO GET lIST OF BUDGET CATEGORIES BEING MET FOR GIVEN MONTH #####################################################
    varA = 1 #user id
    varB = 1 #month
    varC = 2021 #year

    cursor.execute("SELECT c.category as category FROM (SELECT b.category, IFNULL(a.total_amount, 0) AS amount_spent, b.budget FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-02' AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND nr.user_id = %s) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category) c WHERE c.amount_spent <= c.budget", [varA, varB, varC, varA, varA])
    categoriesBeingMet = cursor.fetchall()
    categories = [item[0] for item in amountPerCategoryForMonth]
    # spending = [item[1] for item in amountPerCategoryForMonth]

    numCategoriesBeingMet = len(categoriesBeingMet)
    ################################## END OF MYSQL QUERY 3 ######################################################################################################################3


    ################################### START OF MYSQL QUERY 4 TO FIND AMOUNT LEFT TO SPEND IN EACH CATEGORY FOR A PARTICULAR MONTH #################################################
    varA = 1 #user id
    varB = 1 #month
    varC = 2021 #year
    cursor.execute("SELECT b.category, GREATEST(b.budget - IFNULL(a.total_amount, 0), 0) AS amount_left_to_spend  FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-00' AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND nr.user_id = %s) t GROUP BY t.category) a  RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category", [varA, varB, varC, varA, varA])
    amountLeftPerCategory = cursor.fetchall()
    categories = [item[0] for item in amountLeftPerCategory]
    amount_left = [item[1] for item in amountLeftPerCategory]

    # labels = categories
    # outer_values = budget
    # inner_values = amount_left
    #
    # Money_left_to_spend = go.Pie(
    #     hole=0.2,
    #     sort=False,
    #     direction='clockwise',
    #     values=inner_values,
    #     labels=labels,
    #     textinfo='label',
    #     textposition='inside',
    #     marker={'line': {'color': 'white', 'width': 1}}
    # )
    #
    # Budget = go.Pie(
    #     hole=0.8,
    #     sort=False,
    #     direction='clockwise',
    #     values=outer_values,
    #     labels=labels,
    #     textinfo='label',
    #     textposition='inside',
    #     marker={'line': {'color': 'white', 'width': 1}}
    # )
    #
    # fig = go.FigureWidget(data=[Money_left_to_spend, Budget])
    #
    # fig.layout.update(title="Money left to spend", paper_bgcolor='rgba(0,0,0,0)',
    # plot_bgcolor='rgba(0,0,0,0)',
    # # legend=dict(x=-.1, y=1.2),
    # width=750,
    # height=750, font=dict(family="Calibri", size=16, color="#ffffff"))

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        y=categories,
        x=spending,
        name='Amount Spent',
        orientation='h',
        marker=dict(
            color='red',
            line=dict(color='red', width=3)
        )
    ))
    fig1.add_trace(go.Bar(
        y=categories,
        x=amount_left,
        name='Left to spend',
        orientation='h',
        marker=dict(
            color='green',
            line=dict(color='green', width=3)
        )
    ))

    fig1.layout.update(barmode='stack', title="Money left to spend for Current Month", paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Amount (in $)",
    width=550,
    height=450, font=dict(family="Calibri", size=16, color="#ffffff"))

    fig1.update_yaxes(automargin=True)

    money_left_to_spend_graph = plot(fig1, output_type='div')
    ############################## END OF MYSQL QUERY 4 ##################################################################################################################################

    #############################START OF MYSQL QUERY 5 TO GET TOTAL AMOUNT SPENT OF OTHER USER WITH SIMILAR BUDGET #########################################################################
    varA = 1 #user id
    varB = 1 #month
    varC = 2021 #year
    cursor.execute("SELECT @user_budget := total_amount_under_per_month from customhome_budgetinfo WHERE user_id = %s LIMIT 1", [varA])
    cursor.execute("SELECT t.user_id, SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-02' AND user_id = (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1) LIMIT 1) UNION ALL SELECT amount, user_id FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND user_id = (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1) LIMIT 1)) t GROUP BY t.user_id", [varA, varB, varC, varA])
    preProcessedTuple = cursor.fetchall() #tuple index 0 is OTHER userid and index 1 is total amount spent by other user/ideal user with similar budget to current user
    similarUserAmountSpent = preProcessedTuple[0][1]
    similarUserAmountSpent = float(similarUserAmountSpent)
    similarUserAmountSpent = round(similarUserAmountSpent, 2)
    ############################## END OF MYSQL QUERY 5 #######################################################################################################################################

    ##############################START OF MYSQL QUERY 6/AF1 TO GET SPENDING HABITS OF IDEAL USER ##############################################################################################
    varA = 1 #userID
    varB = 1 #month
    varC = 2021 #year
    cursor.execute("SELECT @user_budget := total_amount_under_per_month from customhome_budgetinfo WHERE user_id = %s LIMIT 1", [varA])
    cursor.execute("SELECT @other_user := t.user_id FROM (SELECT (frequency/12)*amount AS amount, user_id FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-02' AND user_id = (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1) LIMIT 1) UNION ALL SELECT amount, user_id FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND user_id = (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1) LIMIT 1)) t GROUP BY t.user_id", [varA, varB, varC, varA])
    cursor.execute("SELECT b.category, IFNULL(a.total_amount, 0) as amt_spent, b.budget FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-00' AND r.user_id = @other_user UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND nr.user_id = @other_user) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = @other_user) b ON a.category = b.category", [varB, varC])

    otherUserSpendingHabits = cursor.fetchall() #tuple(category, amt_spent, budget amount for category)

    categories = [item[0] for item in otherUserSpendingHabits]
    spending = [item[1] for item in otherUserSpendingHabits]
    budget = [item[2] for item in otherUserSpendingHabits]

    fig = go.Figure(data=[
        go.Bar(name='Spending', x=categories, y=spending),
        go.Bar(name='Budget', x=categories, y=budget)
    ])
    # Change the bar mode
    fig.layout.update(title="Similar user's spending",
    yaxis_title="Amount (in $)", barmode='group', paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)', legend=dict(x=-.1, y=1.2), width=570,
    height=500, font=dict(family="Calibri", size=16, color="#ffffff"))

    other_user_spending_graph = plot(fig, output_type='div')
    ############################# END OF MYSQL QUERY 6 ##########################################################################################################################################

    ############################## START OF MYSQL QUERY 7/TOTAL BUDGET PER MONTH ################################################################################################################

    varA = 1 #userID
    cursor.execute("SELECT total_amount_under_per_month from customhome_budgetinfo WHERE user_id = %s LIMIT 1", [varA])
    monthly_budget = cursor.fetchall()
    monthly_budget = [item[0] for item in monthly_budget]
    monthly_budget = monthly_budget[0]

    ############################# END OF MYSQL QUERY 7 ##########################################################################################################################################

    userName = request.user.get_username()
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

    print(actualID)
    # context = {'amount': totalAmountSpentLastMonth, 'CategoryAndBudgetAmounts':amountPerCategoryForMonth, 'categoriesMet':categoriesBeingMet, 'numBudgetCategoriesMet':numCategoriesBeingMet, 'amountLeftPerCategory':amountLeftPerCategory, 'similarUserAmountSpent':similarUserAmountSpent, 'idealSpendingHabits':otherUserSpendingHabits}

# plot_div = plot([Bar(x=x_data, y=y_data,
#                     name='test',
#                     opacity=0.8, marker_color='green')],
#            output_type='div', include_plotlyjs=False, show_link=False, link_text="")

    # fig = go.Figure()
    # scatter = go.Scatter(x=x_data, y=y_data,
    #                      marker = dict(color = ['red'],
    #                                     size = [30]),
    #                                     mode = 'markers')
    # fig.add_trace(scatter)


    # plot_div = plot([Scatter(x=x_data, y=y_data,
    #                     mode='lines', name='test',
    #                     opacity=0.8, marker_color='green')],
    #            output_type='div')

    # for row in resultsFromHomeCursor:
    #     print (row[0], row[1])

    context = {'query_results':results, 'dict': resultsFromHomeCursor, 'money_left_to_spend_graph':money_left_to_spend_graph, 'budget_pie':budget_pie, 'monthly_budget':monthly_budget, 'current_user_spending_graph': current_user_spending_graph, 'other_user_spending_graph':other_user_spending_graph , 'amount': totalAmountSpentLastMonth, 'numBudgetCategoriesMet':numCategoriesBeingMet, 'similarUserAmountSpent':similarUserAmountSpent}
    return render(request, 'CustomHome/homePage.html', context)

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
    form = BudgetInfoForm(user = request.user)
    if request.method == 'POST':
        form = BudgetInfoForm(request.POST, user=request.user)
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
    form = UpdateBudgetInfoForm(instance=budget)

    if request.method == 'POST':
        form = UpdateBudgetInfoForm(request.POST, instance=budget) #we cant JUST pass in request.POST because it will create a new item
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
