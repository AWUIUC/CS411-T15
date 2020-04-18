from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.db import connections

# Create your views here.
@login_required(login_url='CustomHome:login')
def gotoDash(request):
    cursor = connections['default'].cursor()

    ###################################################### START MYSQL QUERY 1 TO GET TOTAL AMOUNT SPENT LAST MONTH FOR THIS USER ONLY ##############################################
    varA = 35; # DO NOT CHANGE
    varB = 6; # DO NOT CHANGE
    cursor.execute("CREATE TABLE tempX(amount DECIMAL(%s, %s), user_id int)", [varA, varB]);
    cursor.execute("CREATE TABLE tempY(amount DECIMAL(%s, %s), user_id int)", [varA, varB]);

    cursor.execute("INSERT INTO tempX(amount, user_id) SELECT (frequency/12)*amount AS amount, user_id FROM customhome_regulartransaction r WHERE r.start_date <= '2021-05-02'");
    cursor.execute("INSERT INTO tempY(amount, user_id) SELECT amount, user_id FROM customhome_nonregulartransaction WHERE month(date) = '5' AND year(date) = '2021'");

    #cursor.execute("SELECT t.user_id, SUM(t.amount) as total_amount FROM (SELECT * FROM tempX UNION ALL SELECT * FROM tempY) t GROUP BY t.user_id");
    varA = 1 #PUT USER ID INSTEAD OF 1 HERE
    cursor.execute("SELECT SUM(t.amount) as total_amount FROM (SELECT * FROM tempX UNION ALL SELECT * FROM tempY) t WHERE t.user_id=%s", [1])

    totalAmountSpentLastMonth = cursor.fetchall()

    cursor.execute("DROP TABLE tempX");
    cursor.execute("DROP TABLE tempY");

    ############################################# END MYSQL QUERY 1 ###############################################################################################################


    ######################################### START OF MYSQL QUERY 2 ##############################################################################################################
    varA = 1 #user id
    varB = 1 #month
    varC = 2021 #year
    cursor.execute("SELECT b.category, IFNULL(a.total_amount, 0) as total_amount, b.budget FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-00' AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND nr.user_id = %s) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category", [varA, varB, varC, varA, varA])

    amountPerCategoryForMonth = cursor.fetchall()
    ##################################### END OF MYSQL QUERY 2 ###################################################################################################################################

    ################################# START OF MYSQL QUERY 3 TO GET lIST OF BUDGET CATEGORIES BEING MET FOR GIVEN MONTH #####################################################
    varA = 1 #user id
    varB = 1 #month
    varC = 2021 #year

    cursor.execute("SELECT c.category as category FROM (SELECT b.category, IFNULL(a.total_amount, 0) AS amount_spent, b.budget FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-02' AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND nr.user_id = %s) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category) c WHERE c.amount_spent <= c.budget", [varA, varB, varC, varA, varA])
    categoriesBeingMet = cursor.fetchall()

    numCategoriesBeingMet = len(categoriesBeingMet)
    ################################## END OF MYSQL QUERY 3 ######################################################################################################################3


    ################################### START OF MYSQL QUERY 4 TO FIND AMOUNT LEFT TO SPEND IN EACH CATEGORY FOR A PARTICULAR MONTH #################################################
    varA = 1 #user id
    varB = 1 #month
    varC = 2021 #year
    cursor.execute("SELECT b.category, GREATEST(b.budget - IFNULL(a.total_amount, 0), 0) AS amount_left_to_spend  FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-00' AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND nr.user_id = %s) t GROUP BY t.category) a  RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = %s) b ON a.category = b.category", [varA, varB, varC, varA, varA])
    amountLeftPerCategory = cursor.fetchall()
    ############################## END OF MYSQL QUERY 4 ##################################################################################################################################

    #############################START OF MYSQL QUERY 5 TO GET TOTAL AMOUNT SPENT OF OTHER USER WITH SIMILAR BUDGET #########################################################################
    varA = 1 #user id
    varB = 1 #month
    varC = 2021 #year
    cursor.execute("SELECT @user_budget := total_amount_under_per_month from customhome_budgetinfo WHERE user_id = %s LIMIT 1", [varA])
    cursor.execute("SELECT t.user_id, SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-02' AND user_id = (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1) LIMIT 1) UNION ALL SELECT amount, user_id FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND user_id = (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1) LIMIT 1)) t GROUP BY t.user_id", [varA, varB, varC, varA])
    preProcessedTuple = cursor.fetchall() #tuple index 0 is OTHER userid and index 1 is total amount spent by other user/ideal user with similar budget to current user
    similarUserAmountSpent = preProcessedTuple[0][1]
    ############################## END OF MYSQL QUERY 5 #######################################################################################################################################

    ##############################START OF MYSQL QUERY 6/AF1 TO GET SPENDING HABITS OF IDEAL USER ##############################################################################################
    varA = 1 #userID
    varB = 1 #month
    varC = 2021 #year
    cursor.execute("SELECT @user_budget := total_amount_under_per_month from customhome_budgetinfo WHERE user_id = %s LIMIT 1", [varA])
    cursor.execute("SELECT @other_user := t.user_id FROM (SELECT (frequency/12)*amount AS amount, user_id FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-02' AND user_id = (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1) LIMIT 1) UNION ALL SELECT amount, user_id FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND user_id = (SELECT DISTINCT b.user_id FROM customhome_budgetinfo b WHERE b.user_id != %s AND b.total_amount_under_per_month > ((@user_budget)*0.9) AND b.total_amount_under_per_month < ((@user_budget)*1.1) LIMIT 1)) t GROUP BY t.user_id", [varA, varB, varC, varA])

    cursor.execute("SELECT b.category, IFNULL(a.total_amount, 0) as amt_spent, b.budget FROM (SELECT t.user_id, t.category ,SUM(t.amount) AS total_amount FROM (SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-00' AND r.user_id = @other_user UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND nr.user_id = @other_user) t GROUP BY t.category) a RIGHT OUTER JOIN (SELECT category, total_amount_under_per_month * (percentage/100) AS budget FROM customhome_budgetinfo WHERE user_id = @other_user) b ON a.category = b.category", [varB, varC])

    otherUserSpendingHabits = cursor.fetchall() #tuple(category, amt_spent, budget amount for category)
    ############################# END OF MYSQL QUERY 6 ##########################################################################################################################################


    context = {'amount': totalAmountSpentLastMonth, 'CategoryAndBudgetAmounts':amountPerCategoryForMonth, 'categoriesMet':categoriesBeingMet, 'numBudgetCategoriesMet':numCategoriesBeingMet, 'amountLeftPerCategory':amountLeftPerCategory, 'similarUserAmountSpent':similarUserAmountSpent, 'idealSpendingHabits':otherUserSpendingHabits}
    return render(request, 'dashboard/dash.html', context)

    ############################################ START OF MYSQL QUERY XYZ TO FIND AMOUNT SPENT PER CATEGORY IN PARTICULAR MONTH ######################################################
    #varA=1 #id
    #varB=1 #month
    #varC=2021 #year
    #cursor.execute("CREATE TABLE tempX(amount DECIMAL(35, 6), user_id INT, category VARCHAR(255))")

    #cursor.execute("INSERT INTO tempX SELECT (frequency/12)*amount AS amount, user_id, category  FROM customhome_regulartransaction r WHERE r.start_date <= '2021-01-00' AND r.user_id = %s UNION ALL SELECT amount, user_id, category FROM customhome_nonregulartransaction nr WHERE month(nr.date) = %s AND year(nr.date) = %s AND nr.user_id = %s", [varA, varB, varC, varA])
    #cursor.execute("SELECT t.user_id, t.category, SUM(t.amount) AS total_amount FROM (SELECT * FROM tempX) t GROUP BY t.category")

    #amountPerCategoryForMonth = cursor.fetchall()

    #cursor.execute("DROP TABLE tempX")
    ######################################### END MYSQL QUERY XYZ #########################################################################################################################
