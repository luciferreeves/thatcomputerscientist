import hashlib
import os
import random
import re
import string
from datetime import datetime
from random import choice
from string import ascii_letters, digits

import requests
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from dotenv import load_dotenv
from haystack.query import SearchQuerySet
from user_agents import parse

from announcements.models import Announcement
from users.forms import RegisterForm, UpdateUserDetailsForm
from users.models import UserProfile
from users.tokens import CaptchaTokenGenerator

from .context_processors import (add_excerpt, add_num_comments, avatar_list,
                                 check_spam, comment_processor,
                                 highlight_code_blocks, recent_posts)
from .models import AnonymousCommentUser, Category, Comment, Post, Tag
from .recommender import next_read

load_dotenv()

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
    return render(request, 'blog/home.html', {'title': 'Home', 'posts': recent_posts(), 'announcements': announcements})

def tags(request):
    tags = Tag.objects.all()
    # add occurance count to each tag
    for tag in tags:
        tag.count = len(Post.objects.filter(tags__name__in=[tag.name], is_public=True))
        tag.pxs = 10 + tag.count * 2 if tag.count < 10 else 30 + tag.count
        tag.pxs = min(tag.pxs, 36)
    tags = sorted(tags, key=lambda x: x.count, reverse=True)
    tags = [tag for tag in tags if tag.count > 0]
    return render(request, 'blog/tags.html', {'title': 'Tags', 'tags': tags})

def tag_posts(request, tag_slug):
    try:
        tag = Tag.objects.get(slug=tag_slug)
    except Tag.DoesNotExist:
        tag = {
            'name': tag_slug,
            'slug': tag_slug,
            'count': 0,
        }
        return render(request, 'blog/tagged.html', {'title': 'Posts Tagged With: ' + tag_slug, 'posts': None, 'tag': tag})
    posts = Post.objects.filter(tags__name__in=[tag.name], is_public=True).order_by('views')
    for post in posts:
        post.excerpt = add_excerpt(post)
        post.num_comments = add_num_comments(post)
    return render(request, 'blog/tagged.html', {'title': 'Posts Tagged With: ' + tag.name, 'posts': posts, 'tag': tag})

def account(request):
    user = request.user
    avatarlist = avatar_list()
    for key in avatarlist:
        avatarlist[key] = [re.sub(r'\.gif$', '', string) for string in avatarlist[key]]
        avatarlist[key].sort(key=natural_keys)
    avatarlist = {k: avatarlist[k] for k in sorted(avatarlist)}

    blinkies = [re.sub(r'\.gif$', '', string) for string in os.listdir('static/images/blinkies')]
    blinkies.sort(key=natural_keys)

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

        return render(request, 'blog/account.html',  {'title': 'Account', 'user_profile': user_profile, 'avatarlist': avatarlist, 'update_form': update_form, 'blinkies': blinkies})
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

        # Get the number of views for this post
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_string)
        user_identifier = f'{ip}_{user_agent.browser.family}_{user_agent.browser.version_string}_{user_agent.os.family}_{user_agent.os.version_string}'
        cache_key = f'post_view_count_{slug}_{user_identifier}'
        view_count = cache.get(cache_key, 0)
        if view_count == 0:
            post.views += 1
            post.save()
            cache.set(cache_key, 1, 60 * 60 * 24 * 7) # 1 week

        # code stored in .ql-syntax class
        soup = BeautifulSoup(post.body, 'html.parser')
        code_blocks = soup.find_all('pre')
        for code_block in code_blocks:
            data_language = code_block.get('data-language')
            if data_language == 'true':
                data_language = None
            code_block.replace_with(BeautifulSoup(highlight_code_blocks(code_block, language=data_language), 'html.parser'))

        # float: right every other image
        images = soup.find_all('img')
        for i in range(len(images)):
            if i % 2 != 0:
                images[i]['style'] = 'float: right; margin-right: 0px; margin-left: 11px;'

        # remove all paragraphs which are: "<p class="ql-align-justify"><br></p>"
        for p in soup.find_all('p', class_='ql-align-justify'):
            if p.find('br') is not None:
                p.decompose()

        # separate the body in two parts -> the first paragraph and the rest
        first_paragraph = soup.find('p')
        if first_paragraph is not None:
            first_paragraph = str(first_paragraph)
            soup.find('p').decompose()

        post.first_paragraph = first_paragraph
        post.body = str(soup)
        post.views = '{:,}'.format(post.views)


        tags = post.tags.all()
        comments = Comment.objects.filter(post=post)
        for comment in comments:
            if comment.user:
                user_profile = UserProfile.objects.get(user=comment.user)
                comment.avatar_url = user_profile.avatar_url
                comment.processed_body = comment_processor(comment.body)

            if comment.anonymous_user:
                user_profile = comment.anonymous_user
                comment.avatar_url = user_profile.avatar
                comment.processed_body = comment_processor(comment.body)

        if post.is_public:
            # modify request.meta description (only text) and image
            request.meta['description'] = BeautifulSoup(first_paragraph, 'html.parser').get_text()
            request.meta['image'] = 'https://thatcomputerscientist.com/ignis/post_image/720/' + str(post.id) + '.gif'

            read_next = next_read(post)

            return render(request, 'blog/post.html', {'title': post.title, 'post': post, 'tags': tags, 'comments': comments, 'view_count': view_count, 'read_next': read_next})
        else:
            if request.user.is_authenticated and request.user.is_superuser or request.user.is_staff:
                return render(request, 'blog/post.html', {'title': post.title, 'post': post, 'tags': tags, 'comments': comments, 'view_count': view_count})
            else:
                raise Http404
    except Post.DoesNotExist:
        raise Http404

def comment(request, slug):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                # check for spam first
                user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
                if user_ip:
                    user_ip = user_ip.split(',')[0]
                else:
                    user_ip = request.META.get('REMOTE_ADDR')
                user_agent_string = request.META.get('HTTP_USER_AGENT', '')
                user_agent = parse(user_agent_string)
                if check_spam(user_ip=user_ip, user_agent=user_agent, comment=request.POST.get('body'), author=request.user.username):
                    messages.error(request, request.POST.get('body'), extra_tags='spam')
                    return redirect(reverse('blog:post', kwargs={'slug': slug}) + '#comment-' + str(comment.id))
                
                # then we continue
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
    
def anon_comment(request, slug):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # not allowed this is anonymous comment form
            return redirect(reverse('blog:post', kwargs={'slug': slug}))
        else:
            anonymous_name = request.POST.get('anonymous-name')
            anonymous_email = request.POST.get('anonymous-email')
            anonymous_token, at = request.POST.get('anonymous-token'), request.POST.get('anonymous-token')
            new_anonymous_token = request.POST.get('new-anonymous-token')
            anonymous_comment = request.POST.get('anonymous-comment')
            # check for spam first
            user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if user_ip:
                user_ip = user_ip.split(',')[0]
            else:
                user_ip = request.META.get('REMOTE_ADDR')
            user_agent_string = request.META.get('HTTP_USER_AGENT', '')
            user_agent = parse(user_agent_string)
            if check_spam(user_ip=user_ip, user_agent=user_agent, comment=anonymous_comment, author=anonymous_name):
                messages.error(request, anonymous_comment, extra_tags='spam')
                return redirect(reverse('blog:post', kwargs={'slug': slug}) + '#new-comment')

            # now continue with the comment
            if not anonymous_name:
                messages.error(request, 'Please enter a name!')
                return redirect(reverse('blog:post', kwargs={'slug': slug}))
            if not anonymous_comment:
                messages.error(request, 'Please enter a comment!')
                return redirect(reverse('blog:post', kwargs={'slug': slug}))
            if not anonymous_email:
                anonymous_email = ''.join(random.choice(string.ascii_lowercase) for i in range(10)) + '@anonymous.thatcomputerscientist.com'
            if not anonymous_token:
                anonymous_token = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
                at = anonymous_token

            # generate a random avatar for the anonymous user
            avatarlist = avatar_list()
            for key in avatarlist:
                avatarlist[key] = [re.sub(r'\.gif$', '', string) for string in avatarlist[key]]
                avatarlist[key].sort(key=natural_keys)
            avatarlist = {k: avatarlist[k] for k in sorted(avatarlist)}
            avatar_dir = choice(list(avatarlist.keys()))
            avatar_file = choice(avatarlist[avatar_dir])
            anonymous_avatar = avatar_dir + '/' + avatar_file
            anonymous_token = hashlib.sha256(anonymous_token.encode('utf-8')).hexdigest()
            try:
                anonymous_user = AnonymousCommentUser.objects.get(email=anonymous_email, token=anonymous_token)
            except AnonymousCommentUser.DoesNotExist:
                anonymous_user = AnonymousCommentUser.objects.create(email=anonymous_email, token=anonymous_token,
            avatar=anonymous_avatar)
            if new_anonymous_token:
                at = new_anonymous_token
                new_anonymous_token = hashlib.sha256(new_anonymous_token.encode('utf-8')).hexdigest()
                anonymous_user.token = new_anonymous_token
                anonymous_user.save()
            
            # update the anonymous user's name if it has changed
            if anonymous_user.name != anonymous_name:
                anonymous_user.name = anonymous_name
                anonymous_user.save()
            
            comment = Comment.objects.create(anonymous_user=anonymous_user, post=Post.objects.get(slug=slug), body=anonymous_comment)

            # redirect to the post with the comment but set the anonymous user cookie
            response = redirect(reverse('blog:post', kwargs={'slug': slug}) + '#comment-' + str(comment.id))
            response.set_cookie('anonymous_name', anonymous_user.name, max_age=60*60*24*365)
            response.set_cookie('anonymous_email', anonymous_user.email, max_age=60*60*24*365)
            response.set_cookie('anonymous_token', at, max_age=60*60*24*365)

            return response

    else:
        return redirect('blog:home')

def edit_comment(request, slug):
    if request.method == 'POST':
        if request.user.is_authenticated:

            try:
                comment = Comment.objects.get(id=request.POST.get('comment_id'))
                # check for spam first
                user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
                if user_ip:
                    user_ip = user_ip.split(',')[0]
                else:
                    user_ip = request.META.get('REMOTE_ADDR')
                user_agent_string = request.META.get('HTTP_USER_AGENT', '')
                user_agent = parse(user_agent_string)
                if check_spam(user_ip=user_ip, user_agent=user_agent, comment=request.POST.get('body'), author=request.user.username):
                    messages.error(request, request.POST.get('body'), extra_tags='spam')
                    return redirect(reverse('blog:post', kwargs={'slug': slug}) + '#comment-' + str(comment.id))
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
    
def anon_edit_comment(request, slug):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # not allowed this is anonymous comment form
            return redirect(reverse('blog:post', kwargs={'slug': slug}))
        else:

            anonymous_token = request.COOKIES.get('anonymous_token')
            if not anonymous_token:
                return HttpResponse('Unauthorized!', status=401)
            try:
                anonymous_token = hashlib.sha256(anonymous_token.encode('utf-8')).hexdigest()
                comment = Comment.objects.get(id=request.POST.get('comment_id'))
                # check for spam first
                user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
                if user_ip:
                    user_ip = user_ip.split(',')[0]
                else:
                    user_ip = request.META.get('REMOTE_ADDR')
                user_agent_string = request.META.get('HTTP_USER_AGENT', '')
                user_agent = parse(user_agent_string)
                if check_spam(user_ip=user_ip, user_agent=user_agent, comment=request.POST.get('body'), author=comment.anonymous_user.name):
                    messages.error(request, request.POST.get('body'), extra_tags='spam')
                    return redirect(reverse('blog:post', kwargs={'slug': slug}) + '#comment-' + str(comment.id))
                if comment.anonymous_user.token == anonymous_token:
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
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def anon_delete_comment(request, slug, comment_id):
    if request.user.is_authenticated:
        # not allowed this is anonymous comment form
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        anonymous_token = request.COOKIES.get('anonymous_token')
        if not anonymous_token:
            return HttpResponse('Unauthorized!', status=401)
        anonymous_token = hashlib.sha256(anonymous_token.encode('utf-8')).hexdigest()
        try:
            comment = Comment.objects.get(id=comment_id, anonymous_user__token=anonymous_token)
            comment.delete()
            return redirect(reverse('blog:post', kwargs={'slug': slug}) + '#comments')
        except Comment.DoesNotExist:
            return HttpResponse('Comment not found!', status=404)

def search(request):
    query = request.GET.get('q')
    search_in = request.GET.getlist('search_in') if request.GET.get('search_in') else ['posts']
    sort_by = request.GET.get('sort_by') if request.GET.get('sort_by') else 'relevance'
    order = request.GET.get('order') if request.GET.get('order') else 'ascending'
    date_range = request.GET.get('date_range') if request.GET.get('date_range') else 'any'
    search_model_map = {
        'posts': Post,
        'users': User,
        'comments': Comment,
    }

    if query:
        search_results = SearchQuerySet().filter(content=query)
        if search_in:
            search_results = search_results.models(*[search_model_map[model] for model in search_in])

        search_results = [result.object for result in search_results]
    else:
        search_results = None

    print(search_results)

    return render(request, 'blog/search.html', {'title': f"Search results for '{query}'", 'query': query, 'search_results': search_results, 'search_in': search_in, 'sort_by': sort_by, 'order': order, 'date_range': date_range})

def articles(request, date=None, cg=None):
    type = 'articles'
    page = request.GET.get('page') if request.GET.get('page') else 1
    order_by = request.GET.get('order_by') if request.GET.get('order_by') else 'date'
    direction = request.GET.get('direction') if request.GET.get('direction') else 'desc'
    categories = Category.objects.all()
    category = request.GET.get('category')
    try:
        page = int(page)
    except:
        page = 1

    posts = Post.objects.filter(is_public=True)

    if date:
        date_month = date.split('_')[0] # month name like 'Decemeber'
        date_year = date.split('_')[1] # year like '2019'
        date_m = datetime.strptime(date_month, '%B').month # convert month name to month number
        posts = Post.objects.filter(is_public=True, date__month=date_m, date__year=date_year)
        type = 'articles-archive'
        date = date_month + ' ' + date_year
    
    if cg:
        cg = str.lower(cg)
        if category and cg != category and category != 'all':
            return redirect(reverse('blog:categories') + '/{}'.format(category))
        category = cg
        posts = Post.objects.filter(is_public=True, category__slug=cg)
        type = 'articles-category'
    

    posts = posts.order_by('-' + order_by) if direction == 'desc' else Post.objects.filter(is_public=True).order_by(order_by)
    if category and category != 'all':
        posts = posts.filter(category__slug=category)
        category_name = Category.objects.get(slug=category).name
    else:
        category = 'all'
    posts = Paginator(posts, 10)
    num_pages = posts.num_pages
    try:
        posts = posts.page(page)
    except:
        posts = posts.page(num_pages)

    for post in posts:
        post.excerpt = add_excerpt(post)
        post.num_comments = add_num_comments(post)
    return render(request, 'blog/articles.html', {'title': 'Articles', 'posts': posts, 'num_pages': num_pages, 'page': page, 'order_by': order_by, 'direction': direction, 'categories': categories, 'category': category, 'category_name': category_name if category != 'all' else '', 'type': type, 'date': date if date else '', 'cg': cg if cg else ''})

def user_activity(request, username):
    try:
        user = User.objects.get(username__iexact=username)
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
    except User.DoesNotExist:
        # return default 404 page
        raise Http404

def archives(request):
    archives = Post.objects.filter(is_public=True).dates('date', 'month', order='DESC')
    return render(request, 'blog/archives.html', {'title': 'Archives', 'archives': archives})

def categories(request):
    categories = Category.objects.all()
    return render(request, 'blog/categories.html', {'title': 'Categories', 'categories': categories})

def policy(request):
    return render(request, 'blog/site_policy.html', {'title': 'Site Policy'})

def socialify(request):
    url = request.GET.get('url') if request.GET.get('url') else None
    if url:
        # convert Github URL to repo owner/name
        if 'github.com' in url:
            url = url.split('github.com/')[1]
            url = url.split('/')
            url = url[0] + '/' + url[1]
    socialify_options = {
        'theme': 'Dark' if not request.GET.get('theme') else request.GET.get('theme'),
        'font': 'Inter' if not request.GET.get('font') else request.GET.get('font'),
        'description': 0 if not request.GET.get('description') else request.GET.get('description'),
        'forks': 0 if not request.GET.get('forks') else request.GET.get('forks'),
        'issues': 0 if not request.GET.get('issues') else request.GET.get('issues'),
        'language_1': 0 if not request.GET.get('language_1') else request.GET.get('language_1'),
        'language_2': 0 if not request.GET.get('language_2') else request.GET.get('language_2'),
        'name': 0 if not request.GET.get('name') else request.GET.get('name'),
        'owner': 1 if not request.GET.get('owner') else request.GET.get('owner'),
        'stargazers': 0 if not request.GET.get('stargazers') else request.GET.get('stargazers'),
        'pulls': 0 if not request.GET.get('pulls') else request.GET.get('pulls'),
        'pattern': 'Plus' if not request.GET.get('pattern') else request.GET.get('pattern'),
    }

    for key, value in socialify_options.items():
        if value == 'on':
            socialify_options[key] = 1
        elif value == 'off':
            socialify_options[key] = 0

    return render(request, 'blog/socialify.html', {'title': 'Socialify', 'options': socialify_options, 'url': url})

def anilist(request):
    return render(request, 'blog/anilist.html', {'title': 'My Anime List'})

@xframe_options_sameorigin
def anidata(request):
    malURL = 'https://myanimelist.net/animelist/crvs'
    MAL = requests.get(malURL)
    MALContent = MAL.content
    MALStatus = MAL.status_code
    
    if MALStatus != 200:
        MALContent = '<html><head><link rel="stylesheet" href="/static/css/styles.css"><style>img { width: 75%; display: block; margin: -20px auto 20px auto; } h1 { text-align: center; } p { text-align: center; } body {background: transparent !important;} </style></head><body><img src="/static/images/site/sad-failure.gif" alt="Sad Failure"><h1>MyAnimeList does not seem to respond at the moment.</h1><p>Maybe, we go <a href="https://myanimelist.net/animelist/crvs" target="_blank">knock on their door</a> instead?</p></body></html>'
    else:
        MALContent = MALContent.decode('utf-8')
        MALParsed = BeautifulSoup(MALContent, 'html.parser')
        # remove script tags
        for tag in MALParsed(['script', 'meta', 'noscript']):
            tag.extract()

        # add myanimelist.net to relative links
        for link in MALParsed.find_all('a'):
            if link.get('href') and link.get('href')[0] == '/':
                link['href'] = 'https://myanimelist.net' + link['href']

            # make all links open in new tab
            link['target'] = '_blank'

        MALContent = MALParsed.prettify()

    return render(request, 'blog/anidata.html', {'title': 'My Anime List', 'MALContent': MALContent})
