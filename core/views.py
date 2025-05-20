from django.shortcuts import render

def home(request):
    request.meta.title = "Home"
    return render(request, "core/home.html")