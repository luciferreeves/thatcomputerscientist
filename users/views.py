from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .accountFunctions import store_token, verify_token
from .forms import UpdateUserDetailsForm
from .mail_send import send_email
from .models import UserProfile


# Create your views here.
def login_user(request):
    # pass
    next = request.POST.get('next', 'blog:home')
    username = request.POST['username']
    password = request.POST['password']
    if username == '' or password == '' or username is None or password is None:
        # required fields are empty
        messages.error(request, 'RFEERR', extra_tags='loginError')
        return HttpResponseRedirect(next + '?username=' + username)
    else: 
        # check if email is verified
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                email_verified = UserProfile.objects.get(user=user.pk).email_verified
            except:
                # user has no profile
                email_verified = False
            if email_verified:
                login(request, user)
                return HttpResponseRedirect(next)
            else:
                # email not verified
                messages.error(request, 'ENVERR', extra_tags='loginError')
                return HttpResponseRedirect(next + '?username=' + username)
        else:
            # invalid credentials
            messages.error(request, 'IUOPERR', extra_tags='loginError')
            return HttpResponseRedirect(next + '?username=' + username)

def logout_user(request):
    logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def update_user(request):
    user = request.user
    if user is not None:
        if request.method == 'POST':
            form = UpdateUserDetailsForm(request.POST, user=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile was successfully updated!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                messages.error(request, 'Unable to update profile! Please try again later.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'You must be logged in to update your profile!')
        return redirect('blog:home')

def delete_user(request):
    user = request.user
    if user is not None:
        if request.method == 'POST':
            password = request.POST['password']
            if user.check_password(password):
                # delete user, all comments, user profile details, and all posts
                user.delete()
                messages.success(request, 'Your account was successfully deleted!')
                return redirect('blog:home')
            else:
                messages.error(request, 'Incorrect password!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Unable to delete account! Please try again later.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'You must be logged in to delete your account!')
        return redirect('blog:home')

def update_avatar(request):
    user = request.user
    if user is not None:
        if request.method == 'POST':
            user_profile = UserProfile.objects.get(user=user)
            user_profile.avatar_url = request.POST['avatar']
            user_profile.save()
            messages.success(request, 'Avatar was successfully updated!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Unable to update avatar! Please try again later.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'You must be logged in to update your avatar!')
        return redirect('blog:home')

def update_blinkie(request):
    user =  request.user
    if user is not None:
        if request.method == 'POST':
            user_profile = UserProfile.objects.get(user=user)
            user_profile.blinkie_url = request.POST['blinkie']
            user_profile.save()
            messages.success(request, 'Blinkie was successfully updated!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Unable to update blinkie! Please try again later.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'You must be logged in to update your blinkie!')
        return redirect('blog:home')
    
def change_password(request):
    username = request.user
    old_password = request.POST['oldPassword']
    new_password = request.POST['newPassword']
    confirm_password = request.POST['confirmPassword']
    if username is not None:
        user = User.objects.get(username=username)
        if user.check_password(old_password):
            if new_password == confirm_password:
                if len(new_password) < 8:
                    messages.error(request, 'The new password must be at least 8 characters long!')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password was successfully changed!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                messages.error(request, 'The new password and confirmation password do not match!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Old password is incorrect!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'Unable to change password! Please try again later.')
        return redirect('blog:home')

def send_change_user_email(request):
    user = request.user
    new_email = request.POST['email']
    if user is not None:
        # Check if the new and the old email are the same
        if user.email == new_email:
            messages.error(request, 'New email is the same as the old one!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # check if email is already in use
        if User.objects.filter(email=new_email).exists():
            messages.error(request, 'Email is already in use!')
            # Redirect to referrer
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # Send verification email
        subject = 'Verify your email address'
        uid, token = store_token(token_type='changeemail', user=user, email=new_email)

        message = render_to_string('email_change_verification_email.html', {
            'user': user.username if user.first_name is None else user.first_name,
            'site_name': 'That Computer Scientist',
            'uid': uid,
            'token': token,
            'protocol': request.scheme + '://',
            'domain': request.get_host(),
        })
        message = strip_tags(message)
        # send_mail(subject, message, 'That Computer Scientist <' + settings.EMAIL_HOST_USER + '>', [new_email])

        if (send_email(sender='noreply@thatcomputerscientist.com', sender_name='That Computer Scientist', recipient=new_email, subject=subject, body_html=message, body_text=message)):
            messages.success(request, 'Verification email was sent! Please check your email.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Unable to change email! Please try again later.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    else:
        messages.error(request, 'Unable to change email! Please try again later.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def send_verification_email(request):
    # this is a post only view
    if request.method == 'POST':
        username = request.POST.get('username')
        subject = 'Verify your email address'
        user = User.objects.get(username=username)
        uid, token = store_token(token_type='verifyemail', user=user, email=user.email)

        message = render_to_string('verification_email.html', {
            'user': user.username if user.first_name is None else user.first_name,
            'site_name': 'That Computer Scientist',
            'uid': uid,
            'token': token,
            'protocol': 'https://' if request.is_secure() else 'http://',
            'domain': request.get_host(),
        })
        message = strip_tags(message)
        if (send_email(sender='noreply@thatcomputerscientist.com', sender_name='That Computer Scientist', recipient=user.email, subject=subject, body_html=message, body_text=message)):
            messages.success(request, 'VESENT', extra_tags='loginError')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'VESENDERR', extra_tags='loginError')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'VESENDERR', extra_tags='loginError')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def verify_email(request, mode, uid, token):
    token_object = verify_token(mode, uid, token)
    redirect_to = reverse('blog:account') + '?tab=email' if mode == 'changeemail' else 'blog:home'
    success_message = 'Email was successfully changed!' if mode == 'changeemail' else 'VESUCCESS'
    error_message = 'Unable to verify email! Please try again later.'

    if token_object is not None and token_object.verified:
        user = User.objects.get(pk=token_object.user_id)
        user.email = token_object.email
        user.save()
        token_object.delete()
        messages.success(request, success_message, extra_tags='loginError' if mode == 'verifyemail' else '')
        return redirect(redirect_to)
    else:
        messages.error(request, error_message)
        return redirect(redirect_to)
    