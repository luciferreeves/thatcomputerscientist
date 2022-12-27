from .models import Post, Category, Comment

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
