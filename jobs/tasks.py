from django.contrib.auth.models import User
from django.utils import timezone

def delete_inactive_users():
    # Delete users who have not verified their email address within 72 hours
    # of registering, ie. email_verified=False and date_joined > 72 hours ago
    users = User.objects.filter(date_joined__lt=timezone.now() - timezone.timedelta(hours=72), userprofile__email_verified=False)
    for user in users:
        print("Deleting user: " + user.username)
        user.delete()
    