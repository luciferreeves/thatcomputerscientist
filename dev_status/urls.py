from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'dev_status'
urlpatterns = [
    path('<str:r>', views.home, name='repo'),
    path('<str:r>/<path:p>', views.home, name='repo-path'),
    path('', RedirectView.as_view(url='thatcomputerscientist'))
]
