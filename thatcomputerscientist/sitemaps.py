from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from services.weblog.models import Category, Post, Tag


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = 'http'

    def items(self):
        return Post.objects.filter(is_public=True).order_by('id')

    def lastmod(self, item):
        return item.date

    def location(self, item):
        return reverse('blog:post', args=[item.slug])

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = 'http'

    def items(self):
        return Category.objects.all().order_by('id')

    def lastmod(self, item):
        return item.created_at

    def location(self, item):
        return '/weblog/categories/%s' % item.slug

class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = 'http'

    def items(self):
        return Tag.objects.all().order_by('id')

    def lastmod(self, item):
        return item.created_at

    def location(self, item):
        return '/weblog/tags/%s' % item.slug

class StaticViewSitemap(Sitemap):
    changefreq = "always"
    priority = 0.9
    protocol = 'http'

    def items(self):
        return ['blog:home', 'blog:register']

    def location(self, item):
        return reverse(item)
