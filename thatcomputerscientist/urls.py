"""thatcomputerscientist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path

from .sitemaps import (CategorySitemap, GithubSitemap, PostSitemap,
                       StaticViewSitemap, TagSitemap)

sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'static': StaticViewSitemap,
    'github': GithubSitemap,
}

handler404 = 'thatcomputerscientist.error_handler.custom_404'

def robots_txt(request):
    content = """User-agent: *
Crawl-delay: 5
Disallow: /repositories/*/
Allow: /repositories/$
"""
    return HttpResponse(content, content_type="text/plain")

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('users', include('users.urls', namespace='users')),
    path('blog-admin', include('blog_admin.urls', namespace='blog-admin')),
    path('repositories', include(('dev_status.urls', 'dev_status'), namespace='dev_status')),
    path('ignis', include(('ignis.urls', 'ignis'), namespace='ignis')),
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
