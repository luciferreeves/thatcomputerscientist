from django.db import models
from blog.models import Post

# Create your models here.
class Object(models.Model):
    md5 = models.CharField(max_length=32)
    metadata = models.CharField(max_length=255)
    data = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    location = models.OneToOneField(
        'ObjectDirectory',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.md5

class ObjectDirectory(models.Model):
    name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name
