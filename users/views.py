from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token, EmailChangeTokenGenerator
from django.utils.http import urlsafe_base64_decode

# Create your views here.
def login_user(request):
    # pass
    next = request.POST.get('next', '/')
    username = request.POST['username']
    password = request.POST['password']
    print (username, password)
    if username == '' or password == '':
        messages.error(request, 'Please fill in all fields.')
        return HttpResponseRedirect(next + '?username=' + username)
    else: 
        # check if email is verified
        user = authenticate(request, username=username, password=password)
        if user is not None:
            email_verified = UserProfile.objects.get(user=user.pk).email_verified
            if email_verified:
                login(request, user)
                return HttpResponseRedirect(next)
            else:
                messages.error(request, 'EVERR', extra_tags='loginError')
                return HttpResponseRedirect(next + '?username=' + username)
        else:
            messages.error(request, 'Invalid username or password.', extra_tags='loginError')
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
    is_public = False
    email_public = False
    if 'emailPublic' in request.POST:
        email_public = True if request.POST['emailPublic'] == '1' and is_public else False

    if 'isPublic' in request.POST:
        is_public = True if request.POST['isPublic'] == '1' and is_public else False

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

    
def change_password(request):
    username = request.user
    old_password = request.POST['oldPassword']
    new_password = request.POST['newPassword']
    confirm_password = request.POST['confirmPassword']
    if username is not None:
        user = User.objects.get(username=username)
        if user.check_password(old_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password was successfully changed!')
                return redirect('/account')
            else:
                messages.error(request, 'The new password and confirmation password do not match!')
                return redirect('/account')
        else:
            messages.error(request, 'Old password is incorrect!')
            return redirect('/account')
    else:
        messages.error(request, 'Unable to change password! Please try again later.')
        return redirect('/')


def send_verification_email(request):
    username = request.POST['username']
    user = User.objects.get(username=username)
    

    subject = 'Verify your email address'
    message = render_to_string('verification_email.html', {
        'user': user.username if user.first_name is None else user.first_name,
        'site_name': 'That Computer Scientist',
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https://' if request.is_secure() else 'http://',
        'domain': get_current_site(request).domain,
    })
    message = strip_tags(message)
    send_mail(subject, message, 'That Computer Scientist <' + settings.EMAIL_HOST_USER + '>', [user.email])
    messages.success(request, 'Verification email was sent! Please check your email.', extra_tags='loginError')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        user_profile = UserProfile.objects.get(user=user.pk)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user_profile.email_verified = True
        user_profile.save()
        messages.success(request, 'Your email has been verified! You can now login.', extra_tags='loginError')
        return redirect('/')
    else:
        messages.error(request, 'The verification link is invalid!')
        return redirect('/')

def send_change_user_email(request):
    user = request.user
    new_email = request.POST['email']
    if user is not None:
        # check if email is already in use
        if User.objects.filter(email=new_email).exists():
            messages.error(request, 'Email is already in use!')
            # Redirect to referrer
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # Check if the new and the old email are the same
        if user.email == new_email:
            messages.error(request, 'New email is the same as the old one!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # Send verification email
        subject = 'Verify your email address'
        message = render_to_string('email_change_verification_email.html', {
            'user': user.username if user.first_name is None else user.first_name,
            'site_name': 'That Computer Scientist',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': EmailChangeTokenGenerator().encrypt(new_email),
            'protocol': 'https://' if request.is_secure() else 'http://',
            'domain': get_current_site(request).domain,
        })
        message = strip_tags(message)
        send_mail(subject, message, 'That Computer Scientist <' + settings.EMAIL_HOST_USER + '>', [new_email])
        messages.success(request, 'Verification email was sent! Please check your email.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'Unable to change email! Please try again later.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def change_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        new_email = EmailChangeTokenGenerator().decrypt(token)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None:
        user.email = new_email
        user.save()
        messages.success(request, 'Email was successfully changed!')
        return redirect('/account')
    else:
        messages.error(request, 'The verification link is invalid!')
        return redirect('/')


def register(request):
    messages.error(request, 'Registration is currently disabled!', extra_tags='password2Error')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
