from .models import Post, Category

def recent_posts():
    recent_posts = Post.objects.filter(is_public=True).order_by('-date')[1:6]
    return recent_posts

def categories():
    categories = Category.objects.all()
    return categories

def archives():
    archives = Post.objects.filter(is_public=True).dates('date', 'month', order='DESC')
    return archives
