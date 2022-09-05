from http.client import HTTPResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from users.models import UserProfile, CaptchaStore
from urllib.parse import urlparse
import hashlib
from captcha.image import ImageCaptcha
from random import choice
from string import ascii_letters, digits
import base64
import json

# Create your views here.

def home(request):
    return render(request, 'blog/home.html', {'title': 'Home'})

def account(request):
    user = request.user
    if user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=user)
            avatar = hashlib.md5(str(user_profile.gravatar_email).lower().encode('utf-8')).hexdigest() if user_profile.gravatar_email else hashlib.md5(str(user.email).lower().encode()).hexdigest()
            user_subdomain_url = None
            if user_profile.is_public:
                print(request.scheme)
                scheme = request.is_secure() and "https" or "http"
                domain = urlparse(request.build_absolute_uri()).netloc
                user_subdomain_url = '{}://{}.{}'.format(scheme, user.username, domain)
        except UserProfile.DoesNotExist:
            user_profile = None
            avatar = hashlib.md5(str(user.email).lower().encode()).hexdigest()
        return render(request, 'blog/account.html', {'title': 'Account', 'user_profile': user_profile, 'avatar': avatar, 'user_subdomain_url': user_subdomain_url})
    else:
        # Redirect to login page
        return redirect('/')

def homepage(request):
    return render(request, 'blog/homepage.html', {'title': 'Homepage'})


def get_base64_captcha():
    image = ImageCaptcha()
    random_string = ''.join([choice(ascii_letters + digits) for n in range(6)])
    data = image.generate(random_string)
    base64_data = "data:image/png;base64," + base64.b64encode(data.getvalue()).decode()
    return base64_data, random_string

def register(request):
    csrf_token = request.META.get('CSRF_COOKIE')
    base64_data, random_string = get_base64_captcha()
    try:
        # Delete old captcha
        CaptchaStore.objects.get(csrf_token=csrf_token).delete()
    except CaptchaStore.DoesNotExist:
        pass
    # Create new captcha
    CaptchaStore.objects.create(captcha_string=random_string, csrf_token=csrf_token)
    return render(request, 'blog/register.html', {'title': 'Register New User', 'captcha': base64_data})


def refresh_captcha(request):
    csrf_token = request.META.get('CSRF_COOKIE')
    if not csrf_token or not request.META.get('HTTP_REFERER') or request.META.get('HTTP_REFERER').split('/')[-2] != 'register':
        response_data = {'status': 'error', 'message': 'Unauthorized!'}
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
    base64_data, random_string = get_base64_captcha()
    try:
        CaptchaStore.objects.get(csrf_token=csrf_token).delete()
    except CaptchaStore.DoesNotExist:
        pass

    CaptchaStore.objects.create(captcha_string=random_string, csrf_token=csrf_token)
    response_data = {'captcha': base64_data}
    return HttpResponse(json.dumps(response_data), content_type="application/json")
