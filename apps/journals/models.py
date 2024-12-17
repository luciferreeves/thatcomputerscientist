from django.db import models
from django.conf import settings


class Journal(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=256, unique=True)
    description = models.TextField(blank=True)
    private = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="shared_journals",
        blank=True,
    )
    custom_css = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class JournalEntry(models.Model):
    journal = models.ForeignKey(
        Journal,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    title = models.CharField(max_length=128)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
