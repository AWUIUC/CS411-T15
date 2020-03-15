from django.urls import include, path
from . import views
app_name = 'CustomHome'
urlpatterns = [
    #path('register/', views.registerPage, name='register'),
    path('', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('home/', views.homePage, name='home'),
    path('logout/', views.logoutUser, name='logout'),
]
