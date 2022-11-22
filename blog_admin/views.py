import base64
from django.shortcuts import render, redirect
from users.models import UserProfile
from django.contrib.auth.models import User
from django.contrib import messages
from blog.models import Post, Category, Tag
import re

# Create your views here.

def posts(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        page = request.GET.get('page') if request.GET.get('page') else 1
        try:
            page = int(page)
        except:
            page = 1
        posts = Post.objects.all()[(page-1)*50:page*50]
        num_pages = Post.objects.all().count() // 50 + 1
        url_to_render = 'blog_admin/posts.html?page={}'.format(page) if int(page) and int(page) > 1 else 'blog_admin/posts.html'
        return render(request, url_to_render, { 'title': 'Manage Posts', 'posts': posts, 'num_pages': num_pages, 'page': page })
    else:
        return redirect('blog:home')

def posts_search(request):
    q = request.GET.get('q')
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        if q:
            try:
                # Get the posts where title or body or author or category or tags or slug contains q or the post id is int(q)
                posts = Post.objects.filter(title__icontains=q) | Post.objects.filter(body__icontains=q) | Post.objects.filter(author__username__icontains=q) | Post.objects.filter(category__name__icontains=q) | Post.objects.filter(tags__name__icontains=q) | Post.objects.filter(slug__icontains=q) | Post.objects.filter(id = int(q))
            except:
                # Get the posts where title or body or author or category or tags or slug contains q
                posts = Post.objects.filter(title__icontains=q) | Post.objects.filter(body__icontains=q) | Post.objects.filter(author__username__icontains=q) | Post.objects.filter(category__name__icontains=q) | Post.objects.filter(tags__name__icontains=q) | Post.objects.filter(slug__icontains=q)

            return render(request, 'blog_admin/posts.html', { 'title': 'Search Results for "{}"'.format(q), 'posts': posts })
        else:
            return redirect('blog-admin:posts')
    else:
        return redirect('blog:home')

def new_post(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        categories = Category.objects.all()
        if request.method == 'POST':
            title = request.POST.get('title')
            body = request.POST.get('body')
            body = re.sub(r'<p><br></p>', '', body)
            body = re.sub(r'<p class="ql-align-justify"><br></p>', '', body)
            body = re.sub(r'<p class="ql-align-center"><br></p>', '', body)
            category = request.POST.get('category')
            tags = request.POST.get('tags')
            slug = request.POST.get('slug')
            post_image = request.FILES['post_image'] if 'post_image' in request.FILES else None
            if title and body and category and tags and slug and post_image:
                try:
                    category = Category.objects.get(slug = category)
                    tags = tags.split(',')
                    tags = [tag.strip() for tag in tags]
                    tags = [Tag.objects.get_or_create(slug = tag, name = tag)[0] for tag in tags]
                    post = Post.objects.create(title = title, body = body, category = category, slug = slug, author = request.user)
                    post.tags.set(tags)
                    # convert post_image to base64 and save it in post.post_image
                    post_image = post_image.read()
                    post_image = base64.b64encode(post_image)
                    post.post_image = "data:image/png;base64," + post_image.decode('utf-8')
                    post.save()
                    messages.success(request, 'Post created successfully!')
                    return redirect('blog-admin:posts')
                except Exception as e:
                    messages.error(request, 'Error: {}'.format(e), extra_tags='new_post_create_error')
                    return render(request, 'blog_admin/new_post.html', { 'title': 'New Post', 'categories': categories, 'blog_title': title, 'blog_body': body, 'blog_category': category, 'blog_tags': tags, 'blog_slug': slug })
            else:
                messages.error(request, 'Error: All fields are required!', extra_tags='new_post_create_error')
                return render(request, 'blog_admin/new_post.html', { 'title': 'New Post', 'categories': categories, 'blog_title': title, 'blog_body': body, 'blog_category': category, 'blog_tags': tags, 'blog_slug': slug })
        else:
            return render(request, 'blog_admin/new_post.html', { 'title': 'New Post', 'categories': categories })
    else:
        return redirect('blog:home')

def edit_post(request, slug):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        categories = Category.objects.all()
        post = Post.objects.get(slug = slug)
        if request.method == 'POST':
            title = request.POST.get('title')
            body = request.POST.get('body')
            body = re.sub(r'<p><br></p>', '', body)
            body = re.sub(r'<p class="ql-align-justify"><br></p>', '', body)
            body = re.sub(r'<p class="ql-align-center"><br></p>', '', body)
            category = request.POST.get('category')
            tags = request.POST.get('tags')
            slug = request.POST.get('slug')
            post_image = request.FILES['post_image'] if 'post_image' in request.FILES else None
            if title and body and category and tags and slug:
                try:
                    category = Category.objects.get(slug = category)
                    tags = tags.split(',')
                    tags = [tag.strip() for tag in tags]
                    tags = [Tag.objects.get_or_create(slug = tag, name = tag)[0] for tag in tags]
                    post.title = title
                    post.body = body
                    post.category = category
                    post.slug = slug
                    post.author = request.user
                    post.tags.set(tags)
                    if post_image:
                        # convert to data string src and save it in post.post_image
                        post_image = post_image.read()
                        post_image = base64.b64encode(post_image)
                        post.post_image = "data:image/png;base64," + post_image.decode('utf-8')
                    post.save()
                    messages.success(request, 'Post edited successfully!')
                    return redirect('blog-admin:posts')
                except Exception as e:
                    messages.error(request, 'Error: {}'.format(e), extra_tags='edit_post_create_error')
                    return render(request, 'blog_admin/edit_post.html', { 'title': 'Edit Post', 'categories': categories, 'blog_title': title, 'blog_body': body, 'blog_category': category, 'blog_tags': tags, 'blog_slug': slug, 'post': post })
            else:
                messages.error(request, 'Error: All fields are required!', extra_tags='edit_post_create_error')
                return render(request, 'blog_admin/edit_post.html', { 'title': 'Edit Post', 'categories': categories, 'blog_title': title, 'blog_body': body, 'blog_category': category, 'blog_tags': tags, 'blog_slug': slug, 'post': post })
        else:
            return render(request, 'blog_admin/edit_post.html', { 'title': 'Edit Post', 'categories': categories, 'blog_title': post.title, 'blog_body': post.body, 'blog_category': post.category.slug, 'blog_tags': ','.join([tag.slug for tag in post.tags.all()]), 'blog_slug': post.slug, 'post': post })
    else:
        return redirect('blog:home')

def publish_post(request, slug):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        post = Post.objects.get(slug = slug)
        post.is_public = True
        post.save()
        messages.success(request, 'Post published successfully!')
        return redirect('blog-admin:posts')
    else:
        return redirect('blog:home')

def unpublish_post(request, slug):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        post = Post.objects.get(slug = slug)
        post.is_public = False
        post.save()
        messages.success(request, 'Post unpublished successfully!')
        return redirect('blog-admin:posts')
    else:
        return redirect('blog:home')

def comments(request):
    pass

def categories(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        page = request.GET.get('page') if request.GET.get('page') else 1
        try:
            page = int(page)
        except:
            page = 1
        categories = Category.objects.all()[(page-1)*50:page*50]
        num_pages = Category.objects.all().count() // 50 + 1
        url_to_render = 'blog_admin/categories.html?page={}'.format(page) if int(page) and int(page) > 1 else 'blog_admin/categories.html'
        return render(request, url_to_render, { 'title': 'Manage Categories', 'categories': categories, 'num_pages': num_pages, 'page': page })
    else:
        return redirect('blog:home')

def new_category(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        if request.method == 'POST':
            name = request.POST.get('name')
            slug = request.POST.get('slug')
            description = request.POST.get('description') if request.POST.get('description') else ''
            if name and slug:
                try:
                    category = Category.objects.create(name = name, slug = slug, description = description)
                    messages.success(request, 'Category created successfully!')
                    return redirect('blog-admin:categories')
                except Exception as e:
                    messages.error(request, 'Error: {}'.format(e), extra_tags='new_category_create_error', data = { 'name': name, 'slug': slug, 'description': description })
                    return redirect('blog-admin:new-category')
            else:
                messages.error(request, 'Error: All fields are required!', extra_tags='new_category_create_error', data = { 'name': name, 'slug': slug, 'description': description })
                return redirect('blog-admin:new-category')
        else:
            return render(request, 'blog_admin/new_category.html', { 'title': 'New Category' })
    else:
        return redirect('blog:home')

def edit_category(request, slug):
    pass

def delete_category(request, slug):
    pass

def tags(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        page = request.GET.get('page') if request.GET.get('page') else 1
        try:
            page = int(page)
        except:
            page = 1
        tags = Tag.objects.all()[(page-1)*50:page*50]
        num_pages = Tag.objects.all().count() // 50 + 1
        # add post count to each tag
        for tag in tags:
            # post_count which contain this tag slug
            post_count = Post.objects.filter(tags__slug = tag.slug).count()
            tag.post_count = post_count
        url_to_render = 'blog_admin/tags.html?page={}'.format(page) if int(page) and int(page) > 1 else 'blog_admin/tags.html'
        return render(request, url_to_render, { 'title': 'Manage Tags', 'tags': tags, 'num_pages': num_pages, 'page': page })
    else:
        return redirect('blog:home')

def new(request):
    pass

def users(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        page = request.GET.get('page') if request.GET.get('page') else 1
        try:
            page = int(page)
        except:
            page = 1
        users = User.objects.filter(is_superuser=False)[(page-1)*50:page*50]
        num_pages = User.objects.filter(is_superuser=False).count() // 50 + 1
        url_to_render = 'blog_admin/users.html?page={}'.format(page) if int(page) and int(page) > 1 else 'blog_admin/users.html'
        return render(request, url_to_render, { 'title': 'Manage Users', 'normal_users': users, 'num_pages': num_pages, 'page': page })
    else:
        return redirect('blog:home')

def users_search(request):
    q = request.GET.get('q')
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        if q:
            try:
                # Get the normal users where username or email or first_name or last_name contains q or the user id is int(q)
                users = User.objects.filter(is_superuser=False).filter(username__icontains=q) | User.objects.filter(is_superuser=False).filter(email__icontains=q) | User.objects.filter(is_superuser=False).filter(first_name__icontains=q) | User.objects.filter(is_superuser=False).filter(last_name__icontains=q) | User.objects.filter(is_superuser=False).filter(id = int(q))
            except:
                # Get the normal users where username or email or first_name or last_name contains q
                users = User.objects.filter(is_superuser=False).filter(username__icontains=q) | User.objects.filter(is_superuser=False).filter(email__icontains=q) | User.objects.filter(is_superuser=False).filter(first_name__icontains=q) | User.objects.filter(is_superuser=False).filter(last_name__icontains=q)

            return render(request, 'blog_admin/users.html', { 'title': 'Search Results for "{}"'.format(q), 'normal_users': users })
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
    else:
        return redirect('blog:home')

def edit_user(request, user_id):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        if request.method == 'POST':
            request_user = request.user
            user = User.objects.get(id=user_id)
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.is_superuser = request.POST.get('is_superuser') == 'on' if request_user.is_superuser else user.is_superuser
            user.is_staff = request.POST.get('is_staff') == 'on' if request_user.is_superuser else user.is_staff
            user.is_active = True if request.POST.get('is_active') == 'on' else False

            # User Profile Data
            try:
                user_profile = UserProfile.objects.get(user=user)
            except:
                user_profile = UserProfile(user=user)
            user_profile.bio = request.POST.get('bio')
            user_profile.location = request.POST.get('location')
            user_profile.gravatar_email = request.POST.get('gravatar_email')
            user_profile.email_verified = True if request.POST.get('email_verified') == 'on' else False

            # Save the user
            try:
                user.save()
                user_profile.save()
                messages.success(request, 'User updated successfully!')
                return redirect('blog-admin:users')
            # maybe user name is taken
            except Exception as e:
                messages.error(request, 'Error: {}'.format(e), extra_tags='edit_user_update_error')
                return redirect('blog-admin:edit-user', user_id=user_id)

        else:
            user = User.objects.get(id=user_id)
            try:
                user_profile = UserProfile.objects.get(user=user)
            except:
                user_profile = None
            return render(request, 'blog_admin/edit_user.html', { 'title': 'Edit User', 'edit_user': user, 'edit_user_profile': user_profile })
    else:
        return redirect('blog:home')