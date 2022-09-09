from django.shortcuts import render, redirect
from users.models import UserProfile
from django.contrib.auth.models import User

# Create your views here.
def users(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        # Get the superusers
        superusers = User.objects.filter(is_superuser=True)
        # Get the normal users
        users = User.objects.filter(is_superuser=False)

        return render(request, 'blog_admin/users.html', { 'title': 'Manage Users', 'super_users': superusers, 'normal_users': users })
    else:
        return redirect('blog:home')

def posts(request):
    pass

def comments(request):
    pass

def categories(request):
    pass

def tags(request):
    pass

def new(request):
    pass

def search(request):
    q = request.GET.get('q')
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        if q:
            try:
                # Get the superusers where username or email or first_name or last_name contains q or the user id is int(q)
                superusers = User.objects.filter(is_superuser=True).filter(username__icontains=q) | User.objects.filter(is_superuser=True).filter(email__icontains=q) | User.objects.filter(is_superuser=True).filter(first_name__icontains=q) | User.objects.filter(is_superuser=True).filter(last_name__icontains=q) | User.objects.filter(is_superuser=True).filter(id = int(q))
                # Get the normal users where username or email or first_name or last_name contains q or the user id is int(q)
                users = User.objects.filter(is_superuser=False).filter(username__icontains=q) | User.objects.filter(is_superuser=False).filter(email__icontains=q) | User.objects.filter(is_superuser=False).filter(first_name__icontains=q) | User.objects.filter(is_superuser=False).filter(last_name__icontains=q) | User.objects.filter(is_superuser=False).filter(id = int(q))
            except:
                # Get the superusers where username or email or first_name or last_name contains q
                superusers = User.objects.filter(is_superuser=True).filter(username__icontains=q) | User.objects.filter(is_superuser=True).filter(email__icontains=q) | User.objects.filter(is_superuser=True).filter(first_name__icontains=q) | User.objects.filter(is_superuser=True).filter(last_name__icontains=q)
                # Get the normal users where username or email or first_name or last_name contains q
                users = User.objects.filter(is_superuser=False).filter(username__icontains=q) | User.objects.filter(is_superuser=False).filter(email__icontains=q) | User.objects.filter(is_superuser=False).filter(first_name__icontains=q) | User.objects.filter(is_superuser=False).filter(last_name__icontains=q)

            return render(request, 'blog_admin/users.html', { 'title': 'Search Results for "{}"'.format(q), 'super_users': superusers, 'normal_users': users })
        else:
            return redirect('blog-admin:users')
    else:
        return redirect('blog:home')