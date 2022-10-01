from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'dev_status'
urlpatterns = [
    path('', views.home, name='home'),
    path('tree/', views.tree, name='roottree'),
    path('tree/<path:path>', views.tree, name='tree'),
    path('raw/<path:path>', views.raw, name='raw'),
]
