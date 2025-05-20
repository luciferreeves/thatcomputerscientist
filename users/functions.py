from users.models import UserProfile

def email_verified(user):
    profile = UserProfile.objects.get(user=user)
    if profile.email_verified:
        return True
    else:
        return False
        