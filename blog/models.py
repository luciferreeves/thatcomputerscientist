import hashlib

from django.conf import settings
from django.db import models
from django.utils.text import slugify

UPLOAD_ROOT = 'images/'

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            self.slug = slugify(self.name)
        return super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            self.slug = slugify(self.name)
        return super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    body = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=False)
    post_image = models.ImageField(upload_to="{}/cover_images".format(UPLOAD_ROOT), blank=True)
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
    views = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            self.slug = slugify(self.title)
        return super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.title)
    
class AnonymousCommentUser(models.Model):
    name = models.CharField(max_length=32)
    email = models.CharField(max_length=32)
    token = models.CharField(max_length=128, unique=True)
    avatar = models.CharField(max_length=128, blank=True)

    @classmethod
    def get_or_create(cls, email, token, avatar=''):
        email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
        token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
        return cls(email=email_hash, token=token_hash, avatar=avatar)
    
    def __str__(self):
        return self.name

class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    anonymous_user = models.ForeignKey(
        'AnonymousCommentUser',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.body[:50] + '...' if len(self.body) > 50 else self.body
