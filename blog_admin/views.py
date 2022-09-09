from django.shortcuts import render, redirect
from users.models import UserProfile
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
def users(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        page = request.GET.get('page') if request.GET.get('page') else 1
        try:
            page = int(page)
        except:
            page = 1
        superusers = User.objects.filter(is_superuser=True)
        users = User.objects.filter(is_superuser=False)[(page-1)*50:page*50]
        num_pages = User.objects.filter(is_superuser=False).count() // 50 + 1
        print(num_pages)
        url_to_render = 'blog_admin/users.html?page={}'.format(page) if int(page) and int(page) > 1 else 'blog_admin/users.html'
        return render(request, url_to_render, { 'title': 'Manage Users', 'super_users': superusers, 'normal_users': users, 'num_pages': num_pages, 'page': page })
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

def new_user(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = request.POST.get('password')
            is_superuser = True if request.POST.get('is_superuser') == 'on' else False
            is_staff = True if request.POST.get('is_staff') == 'on' else False
            is_active = True if request.POST.get('is_active') == 'on' else False

            # User Profile Data
            bio = request.POST.get('bio')
            location = request.POST.get('location')
            gravatar_email = request.POST.get('gravatar_email')
            is_public = False if request.POST.get('is_public') == 'on' else False
            email_public = False if request.POST.get('email_public') == 'on' else False
            email_verified = True if request.POST.get('email_verified') == 'on' else False

            # Create the user
            try:
                user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password, is_superuser=is_superuser, is_staff=is_staff, is_active=is_active)

                # Create the user profile
                user_profile = UserProfile(user=user, bio=bio, location=location, gravatar_email=gravatar_email, is_public=is_public, email_public=email_public, email_verified=email_verified)
                user_profile.save()

                messages.success(request, 'User created successfully!')
                return redirect('blog-admin:users')
            # maybe user name is taken
            except Exception as e:
                messages.error(request, 'Error: {}'.format(e), extra_tags='new_user_create_error')
                return redirect('blog-admin:new-user')

        else:
            return render(request, 'blog_admin/new_user.html', { 'title': 'Create New User' })