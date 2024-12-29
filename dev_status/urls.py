from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "dev_status"
urlpatterns = [
    # path('', views.home, name='home'),
    # path('/<str:r>', views.get_repo, name='repo'),
    # path('/<str:r>/<path:p>', views.get_repo, name='repo-path'),
]
