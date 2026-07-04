from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
import hashlib


class UserProfile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    location = models.CharField(max_length=50, blank=True, verbose_name=_("Location"))
    bio = models.TextField(blank=True, verbose_name=_("Bio"))
    avatar_url = models.TextField(blank=True, verbose_name=_("Avatar URL"))
    is_public = models.BooleanField(default=False, verbose_name=_("Public"))
    email_public = models.BooleanField(default=False, verbose_name=_("Email Public"))
    email_verified = models.BooleanField(default=False, verbose_name=_("Email Verified"))
    blinkie_url = models.TextField(blank=True, default="", verbose_name=_("Blinkie URL"))

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")


class AnonymousCommentUser(models.Model):
    name = models.CharField(max_length=32, verbose_name=_("Name"))
    email = models.CharField(max_length=32, unique=True, verbose_name=_("Email"))
    token = models.CharField(max_length=128, unique=True, verbose_name=_("Token"))
    avatar = models.URLField(max_length=200, blank=True, verbose_name=_("Avatar"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

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
        verbose_name = _("Anonymous User")
        verbose_name_plural = _("Anonymous Users")
