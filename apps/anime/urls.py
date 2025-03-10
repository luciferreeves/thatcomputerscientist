from django.urls import path, re_path

from . import views

app_name = "anime"
urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    re_path(r"^(?P<anime_id>\d+)(?:\.(?P<e>\d+))?/$", views.anime, name="anime"),
]
