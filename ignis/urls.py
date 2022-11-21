from django.urls import path
from . import views

app_name = 'ignis'
urlpatterns = [
    path('/tex', views.tex, name='tex'),
    path('/post_image/<int:post_id>/', views.post_image, name='post_image'),
]
