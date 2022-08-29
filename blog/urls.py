from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('my/', RedirectView.as_view(pattern_name='account', permanent=False)),
    path('account/', RedirectView.as_view(pattern_name='account', permanent=False)),
    path('my/account', views.account, name='account'),
    # path('my/homepage', views.homepage, name='homepage'),
]
