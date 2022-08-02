from django.shortcuts import render, redirect
from users.models import UserProfile
from urllib.parse import urlparse
import hashlib

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
