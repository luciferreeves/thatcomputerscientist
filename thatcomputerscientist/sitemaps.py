import os

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from dotenv import load_dotenv
from github import Github

from apps.blog.models import Category, Post, Tag

load_dotenv()


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = "http"

    def items(self):
        return Post.objects.filter(is_public=True).order_by("id")

    def lastmod(self, obj):
        return obj.date

    def location(self, obj):
        return reverse("blog:post", args=[obj.slug])


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = "http"

    def items(self):
        return Category.objects.all().order_by("id")

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return "/weblog/categories/%s" % obj.slug


class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = "http"

    def items(self):
        return Tag.objects.all().order_by("id")

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return "/weblog/tags/%s" % obj.slug


class StaticViewSitemap(Sitemap):
    changefreq = "always"
    priority = 0.9
    protocol = "http"

    def items(self):
        return ["blog:home", "blog:register"]

    def location(self, item):
        return reverse(item)


class GithubSitemap(Sitemap):
    g = Github(os.getenv("GH_TOKEN"))
    changefreq = "always"
    priority = 0.9
    protocol = "http"

    # get list of all public repos
    public_repos = g.get_user().get_repos(type="public")
    repo_names = []
    for repo in public_repos:
        if "luciferreeves" in repo.full_name:
            repo_names.append(repo.name)

    def items(self):
        return self.repo_names

    def location(self, item):
        return "/repositories/{}".format(item)
