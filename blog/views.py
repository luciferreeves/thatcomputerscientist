from datetime import datetime
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from users.models import UserProfile
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from random import choice
from string import ascii_letters, digits
from .models import Category, Post, Comment
from .context_processors import recent_posts, avatar_list, add_excerpt, add_num_comments, highlight_code_blocks, comment_processor
from announcements.models import Announcement
from users.forms import RegisterForm, UpdateUserDetailsForm
from users.tokens import CaptchaTokenGenerator
from django.contrib import messages
from bs4 import BeautifulSoup
from .forms import PaymentForm
import re
from dotenv import load_dotenv
import os
import stripe
import requests
import math
load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


# Create your views here.

def home(request):
    announcements = Announcement.objects.filter(is_public=True).order_by('-created_at')
    announcements = announcements if len(announcements) > 0 else None
    return render(request, 'blog/home.html', {'title': 'Home', 'recent_posts': recent_posts(), 'announcements': announcements})

def account(request):
    user = request.user
    avatarlist = avatar_list()
    for key in avatarlist:
        avatarlist[key] = [re.sub(r'\.png$', '', string) for string in avatarlist[key]]
        avatarlist[key].sort(key=natural_keys)
    avatarlist = {k: avatarlist[k] for k in sorted(avatarlist)}

    if user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=user)
            if not user_profile.avatar_url:
                # Set a random avatar
                avatar_dir = choice(list(avatarlist.keys()))
                avatar_file = choice(avatarlist[avatar_dir])
                user_profile.avatar_url = avatar_dir + '/' + avatar_file
                user_profile.save()
        except UserProfile.DoesNotExist:
            # Create a new user profile and set a random avatar
            user_profile = UserProfile.objects.create(user=user)
            avatar_dir = choice(list(avatarlist.keys()))
            avatar_file = choice(avatarlist[avatar_dir])
            user_profile.avatar_url = avatar_dir + '/' + avatar_file
            user_profile.save()

        if request.GET.get('tab') == 'details':
            update_form = UpdateUserDetailsForm(user=user, initial={'first_name': user.first_name, 'last_name': user.last_name, 'bio': user_profile.bio, 'is_public': user_profile.is_public, 'email_public': user_profile.email_public, 'location': user_profile.location})
        else:
            update_form = None

        return render(request, 'blog/account.html',  {'title': 'Account', 'user_profile': user_profile, 'avatarlist': avatarlist, 'update_form': update_form})
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
            comment.processed_body = comment_processor(comment.body)

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

def user_activity(request, username):
    user = User.objects.get(username=username)
    user_profile = UserProfile.objects.get(user=user)
    if user_profile.is_public or user == request.user:
        recent_comments = Comment.objects.filter(user=user).order_by('-created_at')[:5]
    else:
        recent_comments = []

    if user_profile.email_public:
        user_email = user.email
    else:
        user_email = ''

    for comment in recent_comments:
        comment.body = comment_processor(comment.body)

    return render(request, 'blog/activity.html', {'title': 'User Activity', 'activity_user': user, 'activity_user_profile': user_profile, 'activity_recent_comments': recent_comments, 'activity_user_email': user_email})

def donate(request):
    amount = request.GET.get('amount')

    if request.GET.get('payment_intent') and request.GET.get('tab') == 'success':
        payment_intent = stripe.PaymentIntent.retrieve(request.GET.get('payment_intent'))
        if payment_intent.status != 'succeeded':
            return redirect(reverse('blog:donate') + '?tab=error&payment_intent=' + payment_intent.id + '&payment_amount=' + str(int(request.GET.get('payment_amount')) / 100) + '&amount=' + str(request.GET.get('amount')) + '&error=' + payment_intent.last_payment_error.message)

    try:
        amount = int(amount)
    except:
        amount = 3
    amount = amount if amount > 0 else 3
    amount = amount if amount < 1000 else 1000
    payment_form = PaymentForm(initial={'amount': amount})

    if request.method == 'POST':
        try:
            # create a payment using stripe
            payment_method = stripe.PaymentMethod.create(
                type='card',
                card={
                    'number': request.POST['card_number'],
                    'exp_month': request.POST['card_expiry_mm'],
                    'exp_year': request.POST['card_expiry_yyyy'],
                    'cvc': request.POST['card_cvv'],
                },
            )

            # get the current usd to inr conversion rate
            rate = requests.get('https://api.exchangerate-api.com/v4/latest/USD').json()['rates']['INR']

            # convert the amount to inr
            init_amt = int(request.POST['amount'])
            amount = init_amt * math.ceil(rate) * 100

            # create a payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='inr',
                payment_method_types=['card'],
                payment_method=payment_method.id,
                confirm=True,
                return_url=request.build_absolute_uri(reverse('blog:donate') + '?tab=success' + '&payment_amount=' + str(int(amount / 100)) + '&amount=' + str(init_amt)),
            )

            if payment_intent.status == 'succeeded':
                return redirect(reverse('blog:donate') + '?tab=success&payment_intent=' + payment_intent.id + '&payment_amount=' + str(int(amount / 100)) + '&amount=' + str(init_amt))
            
            elif payment_intent.status == 'requires_action':
                url = payment_intent['next_action']['redirect_to_url']['url']
                return redirect(url)

                    
            else:
                return redirect(reverse('blog:donate') + '?tab=error&payment_intent=' + payment_intent.id + '&payment_amount=' + str(int(amount / 100)) + '&amount=' + str(init_amt))

        except Exception as e:
            error = e.json_body['error']['message']
            return redirect(reverse('blog:donate') + '?tab=error&payment_amount=' + str(int(amount / 100)) + '&amount=' + str(init_amt) + '&error=' + str(error))

    return render(request, 'blog/donate.html', {'title': 'Donate', 'amount': amount, 'payment_form': payment_form})
