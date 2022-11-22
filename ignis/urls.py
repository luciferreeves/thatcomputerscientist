from django.urls import path
from . import views

app_name = 'ignis'
urlpatterns = [
    path('/tex', views.tex, name='tex'),
    path('/post_image/<int:post_id>/', views.post_image, name='post_image'),
    path('/upload', views.upload_image, name='upload_image'),
    path('/image/<str:slug>/<str:md5>', views.get_image, name='get_image'),
    path('/su/mvdir', views.mvdir, name='mvdir'),
]
