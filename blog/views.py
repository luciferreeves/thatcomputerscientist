from datetime import datetime
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from users.models import UserProfile
from django.core.paginator import Paginator
from random import choice
from string import ascii_letters, digits
from .models import Category, Post, Comment
from .context_processors import recent_posts, avatar_list, add_excerpt, add_num_comments, highlight_code_blocks
from announcements.models import Announcement
from users.forms import RegisterForm
from users.tokens import CaptchaTokenGenerator
from django.contrib import messages
from bs4 import BeautifulSoup
import re

# Create your views here.

def home(request):
    announcements = Announcement.objects.filter(is_public=True).order_by('-created_at')
    announcements = announcements if len(announcements) > 0 else None
    return render(request, 'blog/home.html', {'title': 'Home', 'recent_posts': recent_posts(), 'announcements': announcements})

def account(request):
    user = request.user
    avatarlist = avatar_list()
    if user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=user)
            if not user_profile.avatar_url:
                # Set a random avatar
                avatar_dir = choice(list(avatarlist.keys()))
                avatar_file = choice(avatarlist[avatar_dir])
                user_profile.avatar_url = '/static/images/avatars/' + avatar_dir + '/' + avatar_file
                user_profile.save()
        except UserProfile.DoesNotExist:
            # Create a new user profile and set a random avatar
            user_profile = UserProfile.objects.create(user=user)
            avatar_dir = choice(list(avatarlist.keys()))
            avatar_file = choice(avatarlist[avatar_dir])
            user_profile.avatar_url = '/static/images/avatars/' + avatar_dir + '/' + avatar_file
            user_profile.save()
        return render(request, 'blog/account.html', {'title': 'Account', 'user_profile': user_profile})
    else:
        # Redirect to login page
        return redirect('blog:home')

def register(request):
    user = request.user
    if user.is_authenticated:
        return redirect('blog:account')
    else:
        random_string = ''.join([choice(ascii_letters + digits) for n in range(6)])
        captcha = CaptchaTokenGenerator().encrypt(random_string)
        if request.method == 'POST':
            expected_captcha = CaptchaTokenGenerator().decrypt(request.POST.get('expected_captcha'))
            form = RegisterForm(request.POST, expected_captcha=expected_captcha)
            if form.is_valid():
                form.save(request=request)
                messages.success(request, 'Account was created! Please check your email to verify your account.', extra_tags='accountCreated')
                return redirect('blog:register')
            else:
                return render(request, 'blog/register.html', {'title': 'Register', 'form': form, 'captcha': captcha})
        else:
            form = RegisterForm(expected_captcha=random_string)
            return render(request, 'blog/register.html', {'title': 'Register', 'form': form, 'captcha': captcha})

def post(request, slug):
    try:
        post = Post.objects.get(slug=slug)

        # code stored in .ql-syntax class
        soup = BeautifulSoup(post.body, 'html.parser')
        code_blocks = soup.find_all('pre', class_='ql-syntax')
        for code_block in code_blocks:
            code_block.replace_with(BeautifulSoup(highlight_code_blocks(code_block), 'html.parser'))

        post.body = str(soup)


        tags = post.tags.all()
        comments = Comment.objects.filter(post=post)
        for comment in comments:
            user_profile = UserProfile.objects.get(user=comment.user)
            comment.avatar_url = user_profile.avatar_url

            comment.processed_body = comment.body

            # escape html tags
            comment.processed_body = re.sub(r'<', '&lt;', comment.processed_body)
            comment.processed_body = re.sub(r'>', '&gt;', comment.processed_body)

            # any text between ``` and ``` must be highlighted as code
            code_blocks = re.findall(r'```(.+?)```', comment.processed_body, re.DOTALL)
            for code_block in code_blocks:
                comment.processed_body = comment.processed_body.replace('```' + code_block + '```', highlight_code_blocks(code_block))

            # retain line breaks, for every newline character, add a <br> tag
            comment.processed_body = comment.processed_body.replace('\n', '<br>')

            # replace multiple <br> tags with a single <br> tag
            comment.processed_body = re.sub(r'<br>(\s*<br>)+', '<br><br>', comment.processed_body)

            comment.processed_body = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', comment.processed_body)
            comment.processed_body = re.sub(r'__(.+?)__', r'<i>\1</i>', comment.processed_body)
            comment.processed_body = re.sub(r'~~(.+?)~~', r'<s>\1</s>', comment.processed_body)



        if post.is_public:
            return render(request, 'blog/post.html', {'title': post.title, 'post': post, 'tags': tags, 'comments': comments})
        else:
            if request.user.is_authenticated and request.user.is_superuser or request.user.is_staff:
                return render(request, 'blog/post.html', {'title': post.title, 'post': post, 'tags': tags, 'comments': comments})
            else:
                return HttpResponse('Post not found!', status=404)
    except Post.DoesNotExist:
        return HttpResponse('Post not found!', status=404)

def comment(request, slug):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                post = Post.objects.get(slug=slug)
                if post.is_public:
                    comment = Comment.objects.create(user=request.user, post=post, body=request.POST.get('comment'))
                    return redirect(reverse('blog:post', kwargs={'slug': slug}) + '#comment-' + str(comment.id))
                else:
                    if request.user.is_authenticated and request.user.is_superuser or request.user.is_staff:
                        Comment.objects.create(user=request.user, post=post, body=request.POST.get('comment'))
                        return redirect(reverse('blog:post', kwargs={'slug': slug}) + '#comment-' + str(comment.id))
                    else:
                        return HttpResponse('Post not found!', status=404)
            except Post.DoesNotExist:
                return HttpResponse('Post not found!', status=404)

        else:
            return redirect('blog:home')
    else:
        return redirect('blog:home')

def edit_comment(request, slug):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                comment = Comment.objects.get(id=request.POST.get('comment_id'))
                if comment.user == request.user:
                    comment.body = request.POST.get('body')
                    comment.edited = True
                    comment.edited_at = datetime.now()
                    comment.save()
                    return redirect(reverse('blog:post', kwargs={'slug': slug}) + '#comment-' + str(comment.id))
                else:
                    return HttpResponse('Unauthorized!', status=401)
            except Comment.DoesNotExist:
                return HttpResponse('Comment not found!', status=404)
        else:
            return redirect('blog:home')
    else:
        return redirect('blog:home')

def delete_comment(request, slug, comment_id):
    if request.user.is_authenticated:
        try:
            comment = Comment.objects.get(id=comment_id)
            if comment.user == request.user:
                comment.delete()
                return redirect(reverse('blog:post', kwargs={'slug': slug}) + '#comments')
            else:
                return HttpResponse('Unauthorized!', status=401)
        except Comment.DoesNotExist:
            return HttpResponse('Comment not found!', status=404)
    else:
        return redirect('blog:home')


def search(request):
    categories = Category.objects.all()
    tags = request.GET.get('tags')
    category = request.GET.get('category')
    query = request.GET.get('query')
    search_in_body = False

    # First check for query constraints
    if len(query) == 0:
        return render(request, 'blog/search.html', {'title': 'Search', 'posts': [], 'categories': categories, 'tags': tags, 'cate': category, 'query': query})

    if len(query) < 3:
        return render(request, 'blog/search.html', {'title': 'Search', 'posts': [], 'categories': categories, 'tags': tags, 'cate': category, 'query': query, 'error': 'Query must be at least 3 characters long'})

    if len(query) > 100:
        search_in_body = True

    # public posts which contain the query in the title or body
    posts = Post.objects.filter(is_public=True, title__icontains=query) if not search_in_body else Post.objects.filter(is_public=True, body__icontains=query) | Post.objects.filter(is_public=True, title__icontains=query)

    # filter by category slug
    if category:
        posts = posts.filter(category__slug=category)
    else:
        category = ''

    # filter by tags
    if tags:
        posts = posts.filter(tags__name__in=tags.split(','))
    else:
        tags = ''

    # order by date
    posts = posts.order_by('-date')
    return render(request, 'blog/search.html', {'title': 'Search', 'posts': posts, 'categories': categories, 'tags': tags, 'cate': category, 'query': query})

def articles(request):
    page = request.GET.get('page') if request.GET.get('page') else 1
    order_by = request.GET.get('order_by') if request.GET.get('order_by') else 'date'
    direction = request.GET.get('direction') if request.GET.get('direction') else 'desc'
    categories = Category.objects.all()
    category = request.GET.get('category')
    try:
        page = int(page)
    except:
        page = 1

    posts = Post.objects.filter(is_public=True).order_by('-' + order_by) if direction == 'desc' else Post.objects.filter(is_public=True).order_by(order_by)
    if category and category != 'all':
        posts = posts.filter(category__slug=category)
    else:
        category = 'all'
    posts = Paginator(posts, 10)
    posts = posts.page(page)

    for post in posts:
        post.excerpt = add_excerpt(post)
        post.num_comments = add_num_comments(post)
    num_pages = posts.paginator.num_pages
    return render(request, 'blog/articles.html', {'title': 'Articles', 'posts': posts, 'num_pages': num_pages, 'page': page, 'order_by': order_by, 'direction': direction, 'categories': categories, 'category': category})
