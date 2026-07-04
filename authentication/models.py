from django.conf import settings
from django.db import models
import hashlib


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
    blinkie_url = models.TextField(blank=True, default="")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class AnonymousCommentUser(models.Model):
    name = models.CharField(max_length=32)
    email = models.CharField(max_length=32, unique=True)
    token = models.CharField(max_length=128, unique=True)
    avatar = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_or_create(cls, email, token, avatar=""):
        email_hash = hashlib.md5(email.encode("utf-8")).hexdigest()
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        obj, created = cls.objects.get_or_create(
            email_hash=email_hash, defaults={"token_hash": token_hash, "avatar": avatar}
        )
        return obj

    def __str__(self):
        return f"{self.name} ({self.email[:8]})"

    class Meta:
        verbose_name = "Anonymous Comment User"
        verbose_name_plural = "Anonymous Comment Users"
