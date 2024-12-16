from django.urls import path

from . import views

app_name = "pagoda"
urlpatterns = [
    path("", views.home, name="home"),
    path("m/<str:site_id>", views.site_dashboard, name="site"),
    path("m/<str:site_id>/status", views.check_verification_status, name="site_status"),
    path("m/<str:site_id>/delete", views.delete_site, name="delete_site"),
]
