from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def iq(request):
    return render(request, 'iq.html')

def edu(request):
    return render(request, 'edu.html')

def about(request):
    return render(request, 'about.html')

def maintenance(request):
    return render(request, 'maintenance.html')