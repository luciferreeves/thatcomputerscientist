from django.db import models
from django.conf import settings
# Create your models here.

class Announcement(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    is_public = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)

    def __str__(self):
        return self.content
        
