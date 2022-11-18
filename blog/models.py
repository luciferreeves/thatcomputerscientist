from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    body = models.TextField()
    date = models.DateTimeField()
    post_image = models.TextField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
    )
    tags = models.ManyToManyField('Tag', blank=True)
    is_public = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.date = timezone.now()
        return super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.body
