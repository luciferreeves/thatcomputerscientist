from .models import Post, Category

def recent_posts(request):
    recent_posts = Post.objects.filter(is_public=True).order_by('-date')[:5]
    return {'recent_posts': recent_posts}

def categories(request):
    categories = Category.objects.all()
    return {'categories': categories}

def archives(request):
    archives = Post.objects.filter(is_public=True).dates('date', 'month', order='DESC')
    return {'archives': archives}
