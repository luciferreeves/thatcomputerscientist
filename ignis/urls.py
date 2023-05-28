from django.urls import path

from . import views

app_name = 'ignis'
urlpatterns = [
    path('/tex', views.tex, name='tex'),
    path('/post_image/<int:size>/<str:post_id>', views.post_image, name='post_image'),
    path('/upload', views.upload_image, name='upload_image'),
    path('/image/<post_id>/<image_name>', views.get_image, name='get_image'),
    path('/cover/<str:repository>', views.cover_image, name='cover_image'),
    path('/captcha/<str:captcha_string>', views.captcha_image, name='captcha_image'),
    path('/screenshot', views.get_screenshot, name='screenshot'),
    path('/socialify', views.socialify, name='socialify'),
# def socialify(request, repo, theme, font, pattern, name, description, language_1, language_2, stargazers, forks, issues, pulls):

]
