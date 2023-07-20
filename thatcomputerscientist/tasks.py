from users.models import UserProfile
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def delete_inactive_users():
    # Delete users who have not verified their email address within 72 hours
    # of registering, ie. email_verified=False and date_joined > 72 hours ago

    users = UserProfile.objects.filter(email_verified=False)
    for user in users:
        try:
            current_user = User.objects.get(user=user)
            if current_user.date_joined < timezone.now() - timezone.timedelta(hours=72):
                current_user.delete()
        except:
            pass


def schedule():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_inactive_users, 'interval', hours=1)
    scheduler.start()
