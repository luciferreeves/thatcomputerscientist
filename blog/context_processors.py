from .models import Post, Category, Comment
import os
from django.conf import settings

def recent_posts():
    recent_posts = Post.objects.filter(is_public=True).order_by('-date')[:5]
    for post in recent_posts:
        post.excerpt = post.body.split('>')[1].split('<')[0]
        post.num_comments = Comment.objects.filter(post=post).count()
    return recent_posts

def categories(request):
    categories = Category.objects.all()
    return {'categories': categories}

def archives(request):
    archives = Post.objects.filter(is_public=True).dates('date', 'month', order='DESC')
    return {'archives': archives}

def avatar_list():
    avatar_list = {}
    directory = os.path.join(settings.BASE_DIR, 'static', 'images', 'avatars')
    for directory in os.listdir(directory):
        # ignore hidden files
        if directory.startswith('.'):
            continue
        avatar_list[directory] = os.listdir(os.path.join(settings.BASE_DIR, 'static', 'images', 'avatars', directory))
        # remove hidden files
        for file in avatar_list[directory]:
            if file.startswith('.'):
                avatar_list[directory].remove(file)
    return avatar_list
