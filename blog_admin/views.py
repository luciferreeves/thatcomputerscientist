import re
from datetime import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.core.paginator import Paginator
from blog.models import Category, Post, Tag, Comment

# Create your views here.

def posts(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        page = request.GET.get('page') if request.GET.get('page') else 1
        posts = Post.objects.all().order_by('-date')
        posts = Paginator(posts, 50)
        num_pages = posts.num_pages
        try:
            posts = posts.page(page)
        except:
            posts = posts.page(num_pages)    
        
        return render(request, 'blog_admin/posts.html', { 'title': 'Manage Posts', 'posts': posts, 'num_pages': num_pages, 'page': page })
    else:
        return redirect('blog:home')
    
def comments(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        page = request.GET.get('page') if request.GET.get('page') else 1
        comments = Comment.objects.all().order_by('-created_at')
        comments = Paginator(comments, 50)
        num_pages = comments.num_pages
        try:
            comments = comments.page(page)
        except:
            comments = comments.page(num_pages)

        return render(request, 'blog_admin/comments.html', { 'title': 'Manage Comments', 'comments': comments, 'num_pages': num_pages, 'page': page })

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
        all_tags = [tag.name for tag in Tag.objects.all()]
        if request.method == 'POST':
            title = request.POST.get('title')
            category = request.POST.get('category')
            tags = request.POST.getlist('tags')
            slug = request.POST.get('slug') if request.POST.get('slug') else ''
            post_image = request.FILES['post_image'] if 'post_image' in request.FILES else None
            additional_tags = request.POST.get('additional_tags') if request.POST.get('additional_tags') else ''
            post_date = request.POST.get('post_date') if request.POST.get('post_date') else datetime.now()
            if additional_tags:
                tags += additional_tags.split(',')

            if request.POST.get('post_id'):
                # update post
                try:
                    post_id = int(request.POST.get('post_id'))
                    post = Post.objects.get(id = post_id)
                    
                    post.title = title
                    post.category = Category.objects.get(id = category)
                    post.slug = slug
                    post.tags.set([Tag.objects.get_or_create(name = tag.strip())[0] for tag in tags])
                    post.date = post_date
                    if post_image:
                        post.post_image = post_image
                    post.save()
                    messages.success(request, 'Post updated successfully.')
                    return redirect('blog-admin:posts')
                except Exception as e:
                    messages.error(request, 'Error while updating the post: {}'.format(e), extra_tags='new_post_message')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                if not title or not category or not tags or not post_image:
                    messages.error(request, 'Fields marked with asterisk (*) are required.', extra_tags='new_post_message')
                    return_object = { 'title_value': title, 'category_value': category, 'tags_value': tags, 'slug_value': slug, 'post_image_value': post_image, 'all_tags': all_tags, 'post_date_value': post_date }
                    return render(request, 'blog_admin/new_post.html', { 'title': 'New Post', 'categories': categories, 'return_object': return_object })
                else:
                    # create new post
                    try:
                        post = Post.objects.create(title = title, category = Category.objects.get(id = category), slug = slug, author = request.user, post_image = post_image, date = post_date)
                        post.tags.set([Tag.objects.get_or_create(name = tag.strip())[0] for tag in tags])
                        post.save()
                        return redirect(reverse('blog-admin:edit-post', kwargs = { 'slug': post.slug }))
                    except Exception as e:
                        messages.error(request, 'Some error occured while creating post.', extra_tags='error')
                        return redirect('blog-admin:posts')
            
        else:
            mode = request.GET.get('mode') if request.GET.get('mode') else 'new'
            post_id = request.GET.get('post_id') if request.GET.get('post_id') else None
            try: 
                post = Post.objects.get(id = int(post_id))
            except:
                post_id = None
                mode = 'new'
            if mode == 'edit' and post_id:
                post_tags = [tag.name for tag in post.tags.all()]
                post = { 'id': post.id, 'title': post.title, 'category': post.category.id, 'tags': post_tags, 'slug': post.slug, 'post_image': post.post_image, 'all_tags': all_tags, 'post_date': post.date }
                return render(request, 'blog_admin/new_post.html', { 'title': 'Edit Post', 'categories': categories, 'post': post, 'all_tags': all_tags })

            return render(request, 'blog_admin/new_post.html', { 'title': 'Create New Post', 'categories': categories, 'all_tags': all_tags })
    else:
        return redirect('blog:home')

def edit_post(request, slug):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        post = Post.objects.get(slug = slug)
        if request.method == 'POST':
            body = request.POST.get('body')
            body = re.sub(r'<p><br></p>', '', body)
            body = re.sub(r'<p class="ql-align-justify"><br></p>', '', body)
            try:
                post.body = body
                post.save()
                messages.success(request, 'Post edited successfully!')
                return redirect('blog-admin:posts')
            except Exception as e:
                messages.error(request, 'Error: {}'.format(e), extra_tags='edit_post_create_error')
                return render(request, 'blog_admin/edit_post.html', { 'title': 'Edit Post', 'post': post })

        else:
            return render(request, 'blog_admin/edit_post.html', { 'title': 'Edit Post', 'post': post })
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

