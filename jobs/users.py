from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def delete_inactive_users():
    users = User.objects.filter(
        date_joined__lt=timezone.now() - timezone.timedelta(hours=72),
        userprofile__email_verified=False,
    )

    deleted_count = 0
    for user in users:
        user.delete()
        deleted_count += 1

    return f"Deleted {deleted_count} inactive users"
