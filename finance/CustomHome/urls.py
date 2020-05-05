from django.urls import include, path
from . import views
app_name = 'CustomHome'
urlpatterns = [
    #path('register/', views.registerPage, name='register'),
    path('', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('home/', views.homePage, name='home'),
    path('logout/', views.logoutUser, name='logout'),
    path('insertNonregularTransaction/', views.insertNonregularTransaction, name='insertNonregularTransaction'),
    path('insertRegularTransaction/', views.insertRegularTransaction, name='insertRegularTransaction'),
    path('viewBudget/', views.viewBudgetInfo, name='viewBudgetInfo'),
    path('createBudget/', views.createBudget, name='createBudget'),
    path('updateBudget/<str:pk>/', views.updateBudget, name='updateBudget'),
    path('deleteBudget/<str:pk>/', views.deleteBudget, name='deleteBudget'),
    path('viewRegularTransaction/',views.viewRegularTransaction, name='viewRegularTransaction'),
    path('viewNonregularTransaction/',views.viewNonregularTransaction, name='viewNonregularTransaction'),
    path('updateRegularTransaction/<str:pk>/',views.updateRegularTransaction, name='updateRegularTransaction'),
    path('updateNonregularTransaction/<str:pk>/',views.updateNonregularTransaction, name='updateNonregularTransaction'),
    path('deleteRegularTransaction/<str:pk>/',views.deleteRegularTransaction, name='deleteRegularTransaction'),
    path('deleteNonregularTransaction/<str:pk>/',views.deleteNonregularTransaction, name='deleteNonregularTransaction'),
    path('updateBudgetPercentage/',views.updateBudgetPercentage, name='updateBudgetPercentage'),
    path('updateBudgetAmount/',views.updateBudgetAmount, name='updateBudgetAmount'),
    path('searchNonregular/',views.searchNonregular, name='searchNonregular'),
    path('viewSearchNonregularResult/',views.viewSearchNonregularResult, name='viewSearchNonregularResult'),
]
