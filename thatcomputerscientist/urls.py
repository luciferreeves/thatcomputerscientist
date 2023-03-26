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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import PostSitemap, CategorySitemap, TagSitemap, StaticViewSitemap, GithubSitemap

from PIL import Image
from io import BytesIO
from selenium import webdriver
import time

sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'static': StaticViewSitemap,
    'github': GithubSitemap,
}

handler404 = 'thatcomputerscientist.error_handler.custom_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('users', include('users.urls', namespace='users')),
    path('blog-admin', include('blog_admin.urls', namespace='blog-admin')),
    path('repositories', include(('dev_status.urls', 'dev_status'), namespace='dev_status')),
    path('ignis', include(('ignis.urls', 'ignis'), namespace='ignis')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


def get_screenshot():
    # Configure Selenium WebDriver with headless Chrome options
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1280, 1280)

    url = 'https://www.thatcomputerscientist.com'

    # Wait until the page is loaded
    driver.get(url)
    time.sleep(5)
    
    screenshot = driver.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))

    # Close the browser
    driver.quit()

    # Save as 'siteshot.png'
    screenshot.save('siteshot.png')

get_screenshot()
