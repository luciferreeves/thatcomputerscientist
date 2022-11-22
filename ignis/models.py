from django.db import models
from blog.models import Post
from dotenv import load_dotenv
import os

load_dotenv()
UPLOAD_ROOT = 'images/' if os.getenv('ENVIRONMENT') == 'development' else '/home/ubuntu/database/images/'

# Only For Storing Images

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

