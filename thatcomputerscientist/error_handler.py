import re

# import jellyfish
from django.contrib.auth.models import User
from django.shortcuts import render

# from fuzzywuzzy import process

from apps.blog.models import Post


def get_similar_posts(slug):

    posts = Post.objects.all().filter(is_public=True)
    similar_posts = set()
    # title_choices = [post.title for post in posts]
    # slug_choices = [post.slug for post in posts]

    # title_match = process.extract(slug.replace("-", " "), title_choices, limit=5)
    # slug_match = process.extract(slug, slug_choices, limit=5)

    # for title, score in title_match:
    #     if score > 80:
    #         similar_posts.add(posts.get(title=title))

    # for slug, score in slug_match:
    #     if score > 80:
    #         similar_posts.add(posts.get(slug=slug))

    return similar_posts


def get_similar_users(username):

    users = User.objects.all()
    similar_users = []
    # for user in users:
    # username_similarity = jellyfish.jaro_winkler(username, user.username)
    # if username_similarity > 0.8:
    #     similar_users.append(user)

    return similar_users


def custom_404(request, exception):
    # Your custom 404 view logic here
    context = {
        "mode": "generic",
        "title": "404 Page Not Found",
    }
    path = request.path[1:] if request.path.startswith("/") else request.path

    if (re.fullmatch(r"[\w-]+", path) and "-" in path) or re.fullmatch(
        r"weblog/[\w-]+", path
    ):
        context["mode"] = "article"
        path = path.replace("weblog/", "") if path.startswith("weblog/") else path
        similar_posts = get_similar_posts(path)
        if similar_posts:
            context["similar_posts"] = similar_posts

    if path.startswith("~"):
        context["mode"] = "user"
        username = path[1:]
        similar_users = get_similar_users(username)
        if similar_users:
            context["similar_users"] = similar_users
        context["username"] = username

    return render(
        request,
        "404.html",
        {"context": context, "title": "404 Page Not Found"},
        status=404,
    )
