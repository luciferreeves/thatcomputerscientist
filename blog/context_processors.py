from .models import Post, Category, Comment
import os
from django.conf import settings

def recent_posts():
    recent_posts = Post.objects.filter(is_public=True).order_by('-date')[:5]
    for post in recent_posts:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(post.body, 'html.parser')

        # Create excerpt, count min 1000 characters and max upto next paragraph
        excerpt = ''
        for paragraph in soup.find_all('p'):
            excerpt += str(paragraph)

            if len(excerpt) >= 1000:
                break
        post.excerpt = excerpt


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
