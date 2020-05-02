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
    # cursor.execute("SELECT t.user_id AS name, SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id FROM customhome_regulartransaction r UNION ALL SELECT amount, user_id FROM customhome_nonregulartransaction nr WHERE month(nr.date) = 3) t GROUP BY t.user_id")
    # resultsFromHomeCursor = cursor.fetchall()
    # x_data = [item[0] for item in resultsFromHomeCursor]
    # y_data = [item[1] for item in resultsFromHomeCursor]

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

    cursor.execute("SELECT @date_previous_first_day := DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m-01')") # first day of previous month
    cursor.execute("SELECT @date_previous_last_day := LAST_DAY(NOW() - INTERVAL 1 MONTH)") # last day of previous month

    cursor.execute("SELECT @date_current_first_day := DATE_FORMAT(NOW(), '%Y-%m-01')") # first day of current month
    cursor.execute("SELECT @date_current_last_day := LAST_DAY(NOW())") # last day of current month


    ###################################################### START MYSQL QUERY 1 TO GET TOTAL AMOUNT SPENT LAST MONTH FOR THIS USER ONLY ##############################################
    varA = 35; # DO NOT CHANGE
    varB = 6; # DO NOT CHANGE

    # cursor.execute("DROP TABLE tempX");
    # cursor.execute("DROP TABLE tempY");

    cursor.execute("CREATE TABLE tempX(amount DECIMAL(%s, %s), user_id int)", [varA, varB]);
    cursor.execute("CREATE TABLE tempY(amount DECIMAL(%s, %s), user_id int)", [varA, varB]);

    cursor.execute("INSERT INTO tempX(amount, user_id) SELECT (frequency/12)*amount AS amount, user_id FROM customhome_regulartransaction r WHERE r.start_date <= @date_previous_last_day");
    cursor.execute("INSERT INTO tempY(amount, user_id) SELECT amount, user_id FROM customhome_nonregulartransaction WHERE date BETWEEN @date_previous_first_day AND @date_previous_last_day");

    #cursor.execute("SELECT t.user_id, SUM(t.amount) as total_amount FROM (SELECT * FROM tempX UNION ALL SELECT * FROM tempY) t GROUP BY t.user_id");
    varA = actualID #PUT USER ID INSTEAD OF 1 HERE
    cursor.execute("SELECT SUM(t.amount) as total_amount FROM (SELECT * FROM tempX UNION ALL SELECT * FROM tempY) t WHERE t.user_id=%s", [actualID])

    totalAmountSpentLastMonth = cursor.fetchall()
    arr = [item[0] for item in totalAmountSpentLastMonth]

    totalAmountSpentLastMonth = float(0)

    if arr[0] is not None:
        totalAmountSpentLastMonth = float(arr[0])

    totalAmountSpentLastMonth = round(totalAmountSpentLastMonth, 2)

    cursor.execute("DROP TABLE tempX");
    cursor.execute("DROP TABLE tempY");

    ############################################# END MYSQL QUERY 1 ###############################################################################################################


    ######################################### START OF MYSQL QUERY 2 ##############################################################################################################
    cursor.execute("SELECT b.category, IFNULL(a.total_amount, 0) as total_amount, b.budget FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= @date_previous_last_day AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_previous_first_day AND @date_previous_last_day AND nr.user_id = %s) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category ORDER BY b.category ASC", [varA, varA, varA])

    amountPerCategoryForMonth = cursor.fetchall()
    categories = [item[0] for item in amountPerCategoryForMonth]
    spending_last_month = [item[1] for item in amountPerCategoryForMonth]
    budget = [item[2] for item in amountPerCategoryForMonth]

    fig = go.Figure(data=[
        go.Bar(name='Spending', x=categories, y=spending_last_month),
        go.Bar(name='Budget', x=categories, y=budget)
    ])
    # Change the bar mode
    fig.layout.update(title="Your spending last month",
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
    cursor.execute("SELECT c.category as category FROM (SELECT b.category, IFNULL(a.total_amount, 0) AS amount_spent, b.budget FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= @date_current_last_day AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_current_first_day AND @date_current_last_day AND nr.user_id = %s) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category) c WHERE c.amount_spent <= c.budget", [varA, varA, varA])
    categoriesBeingMet = cursor.fetchall()
    categories = [item[0] for item in amountPerCategoryForMonth]
    # spending = [item[1] for item in amountPerCategoryForMonth]

    numCategoriesBeingMet = len(categoriesBeingMet)
    ################################## END OF MYSQL QUERY 3 ######################################################################################################################3


    ################################### START OF MYSQL QUERY 4 TO FIND AMOUNT LEFT TO SPEND IN EACH CATEGORY FOR A PARTICULAR MONTH #################################################
    cursor.execute("SELECT b.category, GREATEST(b.budget - IFNULL(a.total_amount, 0), 0) AS amount_left_to_spend  FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= @date_current_last_day AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_current_first_day AND @date_current_last_day AND nr.user_id = %s) t GROUP BY t.category) a  RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category", [varA, varA, varA])
    amountLeftPerCategory = cursor.fetchall()
    categories = [item[0] for item in amountLeftPerCategory]
    amount_left = [item[1] for item in amountLeftPerCategory]

    cursor.execute("SELECT b.category, IFNULL(a.total_amount, 0) as total_amount, b.budget FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= @date_current_last_day AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_current_first_day AND @date_current_last_day AND nr.user_id = %s) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category ORDER BY b.category ASC", [varA, varA, varA])

    spending_for_current_month = cursor.fetchall()

    total_amountSpent_currMonth = 0
    for row in spending_for_current_month:
        total_amountSpent_currMonth += row[1]
    total_amountSpent_currMonth = round(total_amountSpent_currMonth, 2)

    spending = [item[1] for item in spending_for_current_month]

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
    cursor.execute("SELECT @curr_user_age := age FROM customhome_customprofile WHERE user_id = %s", [varA])
    cursor.execute("SELECT @age_lowerBound := @curr_user_age - 1")
    cursor.execute("SELECT @age_upperBound := @curr_user_age + 1")

    cursor.execute("SELECT @user_budget := total_amount_under_per_month from customhome_budgetinfo WHERE user_id = %s LIMIT 1", [varA])
    cursor.execute("SELECT i.user_id, SUM(i.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id FROM customhome_regulartransaction r WHERE r.start_date <= @date_previous_last_day AND user_id IN (SELECT t.user_id AS user_id FROM (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1)) t JOIN customhome_customprofile ON t.user_id = customhome_customprofile.user_id WHERE age <= @age_upperBound AND age >= @age_lowerBound) UNION ALL SELECT amount, user_id FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_previous_first_day AND @date_previous_last_day AND user_id IN (SELECT t.user_id AS user_id FROM (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1)) t JOIN customhome_customprofile ON t.user_id = customhome_customprofile.user_id WHERE age <= @age_upperBound AND age >= @age_lowerBound)) i GROUP BY i.user_id", [varA, varA])

    rows = cursor.fetchall()
    similarUserAmountSpent = 0.0

    for row in rows:
        if row[1] > 0:
            similarUserAmountSpent = row[1]
            similarUserAmountSpent = float(similarUserAmountSpent)
            similarUserAmountSpent = round(similarUserAmountSpent, 2)
            break
    #if rows_count > 0:
    #    preProcessedTuple = cursor.fetchall() #tuple index 0 is OTHER userid and index 1 is total amount spent by other user/ideal user with similar budget to current user
    #    similarUserAmountSpent = preProcessedTuple[0][1]
    #    similarUserAmountSpent = float(similarUserAmountSpent)
    #    similarUserAmountSpent = round(similarUserAmountSpent, 2)
    #else:
    #    similarUserAmountSpent = 0.0
    ############################## END OF MYSQL QUERY 5 #######################################################################################################################################

    ##############################START OF MYSQL QUERY 6/AF1 TO GET SPENDING HABITS OF IDEAL USER ##############################################################################################
    cursor.execute("SELECT @user_budget := total_amount_under_per_month from customhome_budgetinfo WHERE user_id = %s LIMIT 1", [varA])
    # cursor.execute("SELECT @other_user := t.user_id FROM (SELECT (frequency/12)*amount AS amount, user_id FROM customhome_regulartransaction r WHERE r.start_date <= @date_previous_last_day AND user_id = (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1) LIMIT 1) UNION ALL SELECT amount, user_id FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_previous_first_day AND @date_previous_last_day AND user_id = (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1) LIMIT 1)) t GROUP BY t.user_id", [varA, varA])
    cursor.execute("SELECT @other_user := t.user_id FROM (SELECT t.user_id AS user_id FROM (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1)) t JOIN customhome_customprofile ON t.user_id = customhome_customprofile.user_id WHERE age <= @age_upperBound AND age >= @age_lowerBound) t LIMIT 1", [varA])

    cursor.execute("SELECT b.category, IFNULL(a.total_amount, 0) as amt_spent, b.budget FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= @date_previous_last_day AND r.user_id = @other_user UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_previous_first_day AND @date_previous_last_day AND nr.user_id = @other_user) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = @other_user) b ON a.category = b.category ORDER BY b.category ASC")

    otherUserSpendingHabits = cursor.fetchall() #tuple(category, amt_spent, budget amount for category)

    categories = [item[0] for item in otherUserSpendingHabits]
    spending = [item[1] for item in otherUserSpendingHabits]
    budget = [item[2] for item in otherUserSpendingHabits]

    fig = go.Figure(data=[
        go.Bar(name='Spending', x=categories, y=spending),
        go.Bar(name='Budget', x=categories, y=budget)
    ])
    # Change the bar mode
    fig.layout.update(title="Similar user's spending last month",
    yaxis_title="Amount (in $)", barmode='group', paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)', legend=dict(x=-.1, y=1.2), width=570,
    height=500, font=dict(family="Calibri", size=16, color="#ffffff"))

    other_user_spending_graph = plot(fig, output_type='div')
    ############################# END OF MYSQL QUERY 6 ##########################################################################################################################################

    ############################## START OF MYSQL QUERY 7/TOTAL BUDGET PER MONTH ################################################################################################################

    cursor.execute("SELECT total_amount_under_per_month from customhome_budgetinfo WHERE user_id = %s LIMIT 1", [varA])
    monthly_budget = cursor.fetchall()
    monthly_budget = [item[0] for item in monthly_budget]
    monthly_budget = monthly_budget[0]

    ############################# END OF MYSQL QUERY 7 ##########################################################################################################################################

    ##############################START OF MYSQL QUERY 8/AF1 TO GET SPENDING HABITS OF AVG USER PER CATEGORY ##############################################################################################

    cursor.execute("SELECT @ids := COUNT(a.user_id) FROM (SELECT DISTINCT user_id FROM customhome_budgetinfo WHERE total_amount_under_per_month BETWEEN (@user_budget*0.9) AND (@user_budget*1.1)) a")

    cursor.execute("CREATE TABLE ids_for_avg(user_id int)")

    cursor.execute("INSERT INTO ids_for_avg(user_id) SELECT t.user_id AS user_id FROM (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1)) t JOIN customhome_customprofile ON t.user_id = customhome_customprofile.user_id WHERE age <= @age_upperBound AND age >= @age_lowerBound", [varA])

    cursor.execute("SELECT b.category, ROUND(IFNULL(a.total_amount, 0), 2) as avg_amount FROM (SELECT t.category, SUM(t.amount)/@ids AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category FROM customhome_regulartransaction r WHERE r.start_date <= @date_previous_last_day AND r.user_id IN (SELECT * FROM ids_for_avg) UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_previous_first_day AND @date_previous_last_day AND nr.user_id IN (SELECT * FROM ids_for_avg)) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category FROM customhome_budgetinfo WHERE user_id = '1') b ON a.category = b.category ORDER BY b.category ASC")

    avgUserSpendingHabits = cursor.fetchall() #tuple(category, amt_spent, budget amount for category)

    categories = [item[0] for item in avgUserSpendingHabits]
    spending = [item[1] for item in avgUserSpendingHabits]

    fig = go.Figure(data=[
        go.Bar(name='Your Spending', x=categories, y=spending_last_month),
        go.Bar(name='Avg User Spending', x=categories, y=spending)
    ])
    # Change the bar mode
    fig.layout.update(title="Average user's spending last month",
    yaxis_title="Amount (in $)", barmode='group', paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)', legend=dict(x=-.1, y=1.2), width=570,
    height=500, font=dict(family="Calibri", size=16, color="#ffffff"))

    avg_user_spending_graph = plot(fig, output_type='div')
    ############################# END OF MYSQL QUERY 8 ##########################################################################################################################################

    ##############################START OF MYSQL QUERY 9/AF1 TO GET TOTAL SPENDING HABITS OF AVG USER ##############################################################################################
    cursor.execute("SELECT SUM(d.avg_amount) FROM (SELECT b.category, ROUND(IFNULL(a.total_amount, 0), 2) as avg_amount FROM (SELECT t.category, SUM(t.amount)/@ids AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category FROM customhome_regulartransaction r WHERE r.start_date <= @date_previous_last_day AND r.user_id IN (SELECT * FROM ids_for_avg) UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_previous_first_day AND @date_previous_last_day AND nr.user_id IN (SELECT * FROM ids_for_avg)) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category FROM customhome_budgetinfo WHERE user_id = '1') b ON a.category = b.category ORDER BY b.category ASC) d")

    avgUserAmountSpent = cursor.fetchall()
    arr = [item[0] for item in avgUserAmountSpent]

    avgUserAmountSpent = float(0)

    if arr[0] is not None:
        avgUserAmountSpent = float(arr[0])

    avgUserAmountSpent = round(avgUserAmountSpent, 2)
    ############################# END OF MYSQL QUERY 9 ##########################################################################################################################################

    ##############################START OF MYSQL QUERY 10/Categories spending more / less than avg user ##############################################################################################
    cursor.execute("SELECT category FROM (SELECT b.category, IFNULL(a.total_amount, 0) as total_amount FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= @date_previous_last_day AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_previous_first_day AND @date_previous_last_day AND nr.user_id = %s) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category ORDER BY b.category ASC) g NATURAL JOIN (SELECT b.category, ROUND(IFNULL(a.total_amount, 0), 2) as avg_amount FROM (SELECT t.category, SUM(t.amount)/@ids AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category FROM customhome_regulartransaction r WHERE r.start_date <= @date_previous_last_day AND r.user_id IN (SELECT * FROM ids_for_avg) UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_previous_first_day AND @date_previous_last_day AND nr.user_id IN (SELECT * FROM ids_for_avg)) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category FROM customhome_budgetinfo WHERE user_id = '1') b ON a.category = b.category ORDER BY b.category ASC) h WHERE g.total_amount >= h.avg_amount", [varA, varA, varA])

    categories_above_avg = cursor.fetchall()
    categories_above_avg = [item[0] for item in categories_above_avg]
    categories_above_avg = ', '.join(categories_above_avg)

    if (categories_above_avg != ''):
        temp1 = 'You need to work on reducing expenses on the '
        temp2 = ' categories!'
        categories_above_avg = temp1 + categories_above_avg + temp2
    else:
        categories_above_avg = ""

    cursor.execute("SELECT category FROM (SELECT b.category, IFNULL(a.total_amount, 0) as total_amount FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= @date_previous_last_day AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_previous_first_day AND @date_previous_last_day AND nr.user_id = %s) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category ORDER BY b.category ASC) g NATURAL JOIN (SELECT b.category, ROUND(IFNULL(a.total_amount, 0), 2) as avg_amount FROM (SELECT t.category, SUM(t.amount)/@ids AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category FROM customhome_regulartransaction r WHERE r.start_date <= @date_previous_last_day AND r.user_id IN (SELECT * FROM ids_for_avg) UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE nr.date BETWEEN @date_previous_first_day AND @date_previous_last_day AND nr.user_id IN (SELECT * FROM ids_for_avg)) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category FROM customhome_budgetinfo WHERE user_id = '1') b ON a.category = b.category ORDER BY b.category ASC) h WHERE g.total_amount < h.avg_amount", [varA, varA, varA])

    categories_below_avg = cursor.fetchall()
    categories_below_avg = [item[0] for item in categories_below_avg]
    categories_below_avg = ', '.join(categories_below_avg)

    if (categories_below_avg != ''):
        temp1 = 'Good Job! The categories you are doing better than average are '
        temp2 = '. Keep going!'
        categories_below_avg = temp1 + categories_below_avg + temp2
    else:
        categories_below_avg = ""

    # print("Good Job! The categories you are doing better than average are", categories_above_avg, "However, you need to work on the", categories_below_avg, "categories")

    cursor.execute("DROP TABLE ids_for_avg")
    ############################# END OF MYSQL QUERY 10 ##########################################################################################################################################


    context = {'query_results':results, 'categories_above_avg':categories_above_avg, 'categories_below_avg':categories_below_avg, 'money_left_to_spend_graph':money_left_to_spend_graph, 'budget_pie':budget_pie, 'monthly_budget':monthly_budget, 'current_user_spending_graph': current_user_spending_graph, 'other_user_spending_graph':other_user_spending_graph, 'avg_user_spending_graph':avg_user_spending_graph, 'avgUserAmountSpent': avgUserAmountSpent, 'amount': totalAmountSpentLastMonth, 'numBudgetCategoriesMet':numCategoriesBeingMet,'CurrUser_CurrMonth_TotalSpending': total_amountSpent_currMonth, 'similarUserAmountSpent':similarUserAmountSpent}
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
    amount = budget[0].total_amount_under_per_month


    #PUTS QUERY RESULTS INTO A DICTIONARY TO BE PASSED IN AS A CONTEXT
    args = {'budget':budget, 'amount':amount, }
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

def updateBudgetAmount(request):
    budget = BudgetInfo.objects.raw('SELECT * FROM customhome_budgetinfo WHERE user_id = %s', [request.user.id])
    amount = budget[0].total_amount_under_per_month
    form = BudgetAmountForm(initial={'amount': amount})

    if request.method=='POST':
        form=BudgetAmountForm(request.POST)
        if form.is_valid():
            new_amount = form.cleaned_data.get('amount')
            uid = request.user.id
            cursor = connection.cursor()
            cursor.execute("UPDATE customhome_budgetinfo SET total_amount_under_per_month=%s WHERE user_id=%s;", [new_amount, uid])
            return redirect('CustomHome:viewBudgetInfo')

    context = {'form':form}
    return render(request, 'CustomHome/updateBudgetAmount.html',context)

def updateBudgetPercentage(request):
    amount = []
    for i in range(9):
        amount.append(BudgetInfo.objects.raw('SELECT * FROM customhome_budgetinfo WHERE user_id = %s AND category = %s', [request.user.id, category_choices[i][0]])[0].percentage)
    form = BudgetPercentageForm(initial={'groceries':amount[0],'education':amount[1],'travel':amount[2],'rnb':amount[3],'bnu':amount[4],'shopping':amount[5],'entertainment':amount[6],'gas':amount[7],'misc':amount[8]})
    if request.method=='POST':
        form=BudgetPercentageForm(request.POST)
        if form.is_valid():
            uid = request.user.id
            cursor = connection.cursor()
            for i in range(9):
                amount[i] = form.cleaned_data.get(category_form_choices[i])
                cursor.execute("UPDATE customhome_budgetinfo SET percentage=%s WHERE user_id=%s AND category = %s", [amount[i], uid, category_choices[i][0]])
            return redirect('CustomHome:viewBudgetInfo')

    context = {'form':form}
    return render(request, 'CustomHome/updateBudgetPercentage.html',context)



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
