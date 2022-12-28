from django.conf import settings
from django.db import models

# User Profile Model
class UserProfile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    location = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    email_public = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

