from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Create your views here.
def login_user(request):
    # pass
    next = request.POST.get('next', '/')
    username = request.POST['username']
    password = request.POST['password']
    print (username, password)
    if username == '' or password == '':
        messages.error(request, 'Please fill in all fields')
        return HttpResponseRedirect(next + '?username=' + username)
    else: 
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print('here3')
            login(request, user)
            return HttpResponseRedirect(next)
        else:
            messages.error(request, 'Invalid username or password')
            print('here4')
            return HttpResponseRedirect(next + '?username=' + username)

def logout_user(request):
    logout(request)
    return redirect('/')
