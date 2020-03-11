from django.shortcuts import render

# Create your views here.
def gotoDash(request):
    return render(request, 'dashboard/dash.html')
