from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from users.models import UserProfile, CaptchaStore
from urllib.parse import urlparse
import hashlib
from captcha.image import ImageCaptcha
from random import choice
from string import ascii_letters, digits
import base64
import json
from .models import Post, Comment
from .context_processors import recent_posts, categories, archives

# Create your views here.

def home(request):
    return render(request, 'blog/home.html', {'title': 'Home', 'recent_posts': recent_posts(), 'categories': categories(), 'archives': archives()})

def account(request):
    user = request.user
    user_subdomain_url = None
    if user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=user)
            avatar = hashlib.md5(str(user_profile.gravatar_email).lower().encode('utf-8')).hexdigest() if user_profile.gravatar_email else hashlib.md5(str(user.email).lower().encode()).hexdigest()
            if user_profile.is_public:
                print(request.scheme)
                scheme = request.is_secure() and "https" or "http"
                domain = urlparse(request.build_absolute_uri()).netloc
                user_subdomain_url = '{}://{}.{}'.format(scheme, user.username, domain)
        except UserProfile.DoesNotExist:
            user_profile = None
            avatar = hashlib.md5(str(user.email).lower().encode()).hexdigest()
        return render(request, 'blog/account.html', {'title': 'Account', 'user_profile': user_profile, 'avatar': avatar, 'user_subdomain_url': user_subdomain_url})
    else:
        # Redirect to login page
        return redirect('blog:home')

def homepage(request):
    return render(request, 'blog/homepage.html', {'title': 'Homepage'})


def get_base64_captcha():
    image = ImageCaptcha()
    random_string = ''.join([choice(ascii_letters + digits) for n in range(6)])
    data = image.generate(random_string)
    base64_data = "data:image/png;base64," + base64.b64encode(data.getvalue()).decode()
    return base64_data, random_string

def register(request):
    user = request.user
    csrf_token = request.META.get('CSRF_COOKIE')
    try:
            # Delete old captcha
            CaptchaStore.objects.get(csrf_token=csrf_token).delete()
    except CaptchaStore.DoesNotExist:
        pass
    if user.is_authenticated:
        return redirect('blog:account')
    else:
        if not csrf_token:
            # Create a new CSRF token
            csrf_token = ''.join([choice(ascii_letters + digits) for n in range(100)])
        base64_data, random_string = get_base64_captcha()
        try:
            # Delete old captcha
            CaptchaStore.objects.get(csrf_token=csrf_token).delete()
        except CaptchaStore.DoesNotExist:
            pass
        # Create new captcha
        CaptchaStore.objects.create(captcha_string=random_string, csrf_token=csrf_token)
        return render(request, 'blog/register.html', {'title': 'Register', 'captcha': base64_data})


def refresh_captcha(request):
    csrf_token = request.META.get('CSRF_COOKIE')
    if not request.META.get('HTTP_REFERER') or request.META.get('HTTP_REFERER').split('/')[-2] != 'register':
        response_data = {'status': 'error', 'message': 'Unauthorized!'}
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
    base64_data, random_string = get_base64_captcha()
    try:
        CaptchaStore.objects.get(csrf_token=csrf_token).delete()
    except CaptchaStore.DoesNotExist:
        pass
    CaptchaStore.objects.create(captcha_string=random_string, csrf_token=csrf_token)
    response_data = {'captcha': base64_data}
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def post(request, slug):
    try:
        post = Post.objects.get(slug=slug)
        tags = post.tags.all()
        comments = Comment.objects.filter(post=post)
        for comment in comments:
            try:
                user_profile = UserProfile.objects.get(user=comment.user)
                comment.avatar = hashlib.md5(str(user_profile.gravatar_email).lower().encode('utf-8')).hexdigest() if user_profile.gravatar_email else hashlib.md5(str(comment.user.email).lower().encode()).hexdigest()
            except UserProfile.DoesNotExist:
                comment.avatar = hashlib.md5(str(comment.user.email).lower().encode()).hexdigest()
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
                    Comment.objects.create(user=request.user, post=post, body=request.POST.get('comment'))
                    return redirect('blog:post', slug=slug)
                else:
                    if request.user.is_authenticated and request.user.is_superuser or request.user.is_staff:
                        Comment.objects.create(user=request.user, post=post, body=request.POST.get('comment'))
                        return redirect('blog:post', slug=slug)
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
                    return redirect('blog:post', slug=slug)
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
                return redirect('blog:post', slug=slug)
            else:
                return HttpResponse('Unauthorized!', status=401)
        except Comment.DoesNotExist:
            return HttpResponse('Comment not found!', status=404)
    else:
        return redirect('blog:home')
