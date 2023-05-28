from django.conf import settings
from django.db import models
from django.utils import timezone

# Create your models here.

class Announcement(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    is_public = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        return super(Announcement, self).save(*args, **kwargs)

    def __str__(self):
        return self.content
        
