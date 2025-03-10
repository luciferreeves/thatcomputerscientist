from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("", views.home, name="home"),
    # My Pages
    path("my/journals/", views.my_journals, name="my_journals"),
]
