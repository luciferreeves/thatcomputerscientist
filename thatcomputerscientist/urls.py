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

# from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path

# from .sitemaps import (CategorySitemap, GithubSitemap, PostSitemap,
#                        StaticViewSitemap, TagSitemap)

# sitemaps = {
#     'posts': PostSitemap,
#     'categories': CategorySitemap,
#     'tags': TagSitemap,
#     'static': StaticViewSitemap,
#     'github': GithubSitemap,
# }

# handler404 = 'thatcomputerscientist.error_handler.custom_404'


def robots_txt(request):
    content = """User-agent: *
Crawl-delay: 5
Disallow: /repositories/*/
Allow: /repositories/$
"""
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    path("", include("core.urls", namespace="core")),
    path("auth", include("authentication.urls", namespace="auth")),
    path("admin", include("administration.urls", namespace="administration")),
    path("admin/administration/", admin.site.urls),
    path("weblog", include("blog.urls", namespace="weblog")),
    path("services", include("services.urls", namespace="services")),
    # path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path("robots.txt", robots_txt),
]

if settings.DEBUG and settings.STATIC_URL:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
