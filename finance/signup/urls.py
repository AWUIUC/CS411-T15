from django.urls import include, path
from . import views
app_name = 'signup'
urlpatterns = [
    path('', views.gotoSignUp, name='signUpPage'),

]
