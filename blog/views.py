from django.shortcuts import render
from users.models import UserProfile
import hashlib

# Create your views here.

def home(request):
    return render(request, 'home.html', {'title': 'Home'})

def account(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        avatar = hashlib.md5(str(user_profile.gravatar_email).lower().encode('utf-8')).hexdigest() if user_profile.gravatar_email else hashlib.md5(str(user.email).lower().encode()).hexdigest()
    except UserProfile.DoesNotExist:
        user_profile = None
        avatar = hashlib.md5(str(user.email).lower().encode()).hexdigest()
    return render(request, 'account.html', {'title': 'Account', 'user_profile': user_profile, 'avatar': avatar})
