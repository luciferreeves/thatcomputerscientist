import base64
from django.shortcuts import render, redirect
from users.models import UserProfile
from django.contrib.auth.models import User
from django.contrib import messages
from blog.models import Post, Category, Tag
from ignis.models import PostImage
import re
import random
import string

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
            posts = Post.objects.filter(title__icontains=q)
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
            random_post_identifier = request.POST.get('random_post_identifier')
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
                    PostImage.objects.filter(temp_post_id = random_post_identifier).update(post = post)
                    PostImage.objects.filter(temp_post_id = random_post_identifier).update(temp_post_id = None)
                    # replace all random_post_identifier with post.id in post.body
                    post.body = post.body.replace(random_post_identifier, str(post.id))
                    post.save()
                    messages.success(request, 'Post created successfully!')
                    return redirect('blog-admin:posts')
                except Exception as e:
                    messages.error(request, 'Error: {}'.format(e), extra_tags='new_post_create_error')
                    return render(request, 'blog_admin/new_post.html', { 'title': 'New Post', 'categories': categories, 'blog_title': title, 'blog_body': body, 'blog_category': category, 'blog_tags': tags, 'blog_slug': slug, 'random_post_identifier': random_post_identifier })    
            else:
                messages.error(request, 'Error: All fields are required!', extra_tags='new_post_create_error')
                return render(request, 'blog_admin/new_post.html', { 'title': 'New Post', 'categories': categories, 'blog_title': title, 'blog_body': body, 'blog_category': category, 'blog_tags': tags, 'blog_slug': slug, 'random_post_identifier': random_post_identifier })
        else:
            # new random temorary post identifier - 8 digit alphanumeric string
            
            random_post_identifier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            random_post_identifier = 'rpi_' + random_post_identifier
            return render(request, 'blog_admin/new_post.html', { 'title': 'New Post', 'categories': categories, 'random_post_identifier': random_post_identifier })
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

