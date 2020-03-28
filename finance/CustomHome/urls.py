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

]
