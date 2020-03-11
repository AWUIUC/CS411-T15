from django.shortcuts import render

# Create your views here.
def gotoLogin(request):
    return render(request, 'login/login.html')
