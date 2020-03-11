from django.urls import include, path
from . import views
app_name = 'login'
urlpatterns = [
    path('', views.gotoLogin, name='loginPage'),

]
