from .models import Post, Category

def recent_posts():
    recent_posts = Post.objects.filter(is_public=True).order_by('-date')[:5]
    for post in recent_posts:
        post.excerpt = post.body.split('>')[1].split('<')[0]
    return recent_posts

def categories():
    categories = Category.objects.all()
    return categories

def archives():
    archives = Post.objects.filter(is_public=True).dates('date', 'month', order='DESC')
    return archives
