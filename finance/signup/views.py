from django.shortcuts import render

# Create your views here.
def gotoSignUp(request):
    return render(request, 'signup/signup.html')
