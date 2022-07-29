from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.models import User


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

def update_user(request):
    username = request.user
    first_name = request.POST['firstname']
    last_name = request.POST['lastname']
    location = request.POST['location']
    gravatar_email = request.POST['gravatarEmail']
    bio = request.POST['bio']
    is_public = True if request.POST['isPublic'] == '1' else False
    email_public = False
    if 'emailPublic' in request.POST:
        email_public = True if request.POST['emailPublic'] == '1' else False

    if username is not None:
        user = User.objects.get(username=username)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        try:
            user_profile = UserProfile.objects.get(user=username)
            user_profile.location = location
            user_profile.gravatar_email = gravatar_email
            user_profile.bio = bio
            user_profile.is_public = is_public
            user_profile.email_public = email_public
            user_profile.save()
        except UserProfile.DoesNotExist:
            user_profile = UserProfile(user=username, location=location, gravatar_email=gravatar_email, bio=bio, is_public=is_public, email_public=email_public)
            user_profile.save()
        messages.success(request, 'Profile was successfully updated!')
        return redirect('/account')
    else:
        messages.error(request, 'Unable to update profile! Please try again later.')
        return redirect('/')

