import base64
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from blog.models import Post, Category, Tag
from ignis.models import CoverImage
import re
from django.http import HttpResponseRedirect

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
            category = request.POST.get('category')
            tags = request.POST.get('tags')
            slug = request.POST.get('slug') if request.POST.get('slug') else ''
            post_image = request.FILES['post_image'] if 'post_image' in request.FILES else None

            if request.POST.get('post_id'):
                # update post
                try:
                    post_id = int(request.POST.get('post_id'))
                    post = Post.objects.get(id = post_id)
                    
                    post.title = title
                    post.category = Category.objects.get(id = category)
                    post.slug = slug
                    post.tags.set([Tag.objects.get_or_create(slug = tag.strip(), name = tag.strip())[0] for tag in tags.split(',')])
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
                    return_object = { 'title_value': title, 'category_value': category, 'tags_value': tags, 'slug_value': slug, 'post_image_value': post_image }
                    return render(request, 'blog_admin/new_post.html', { 'title': 'New Post', 'categories': categories, 'return_object': return_object })
                else:
                    # create new post
                    try:
                        post = Post.objects.create(title = title, category = Category.objects.get(id = category), slug = slug, author = request.user, post_image = post_image)
                        post.tags.set([Tag.objects.get_or_create(slug = tag.strip(), name = tag.strip())[0] for tag in tags.split(',')])
                        post.save()
                        return redirect(reverse('blog-admin:edit-post', kwargs = { 'slug': post.slug }))
                    except Exception as e:
                        print(e)
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
                post_tags = post.tags.all()
                post_tags = [tag.name for tag in post_tags]
                post_tags = ', '.join(post_tags)
                post = { 'id': post.id, 'title': post.title, 'category': post.category.id, 'tags': post_tags, 'slug': post.slug, 'post_image': post.post_image } 
                return render(request, 'blog_admin/new_post.html', { 'title': 'Edit Post', 'categories': categories, 'post': post })

            return render(request, 'blog_admin/new_post.html', { 'title': 'Create New Post', 'categories': categories })
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
                        # update post image to cover image
                        post_image = CoverImage.objects.create(image = post_image, post = post, name = 'cover image for {}'.format(post.slug))
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

