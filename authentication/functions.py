from django.contrib.auth.models import User
from .models import UserProfile


def email_verified(user):
    profile = UserProfile.objects.get(user=user)
    if profile.email_verified:
        return True
    else:
        return False


def get_user_from_username(username):
    user = User.objects.filter(username=username).first()
    if user:
        return user
    return None
