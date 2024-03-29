from django.conf import settings
from django.db import models

from blog.models import Post

UPLOAD_ROOT = 'images/'

# Only For Storing Images

class CoverImage(models.Model):
    image = models.ImageField(upload_to="{}/cover_images".format(UPLOAD_ROOT))
    name = models.CharField(max_length=100, default=None, null=True)
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.name)

class PostImage(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to="{}/post_images".format(UPLOAD_ROOT))
    temp_post_id = models.CharField(max_length=12, default=None, null=True)
    name = models.CharField(max_length=100, default=None, null=True)

    def __str__(self):
        return self.name

class RepositoryTitle(models.Model):
    repository = models.CharField(max_length=100)
    image = models.ImageField(upload_to="{}/repository_titles".format(UPLOAD_ROOT))

    def __str__(self):
        return self.repository

# Delete Files When Deleted From Database

from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, sender=PostImage)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)

@receiver(post_delete, sender=RepositoryTitle)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)

