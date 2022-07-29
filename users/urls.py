from multiprocessing.dummy import Namespace
from django.urls import path
from . import views
from django.contrib import admin

app_name = 'users'
urlpatterns = [
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('update', views.update_user, name='update'),
    path('changepassword', views.change_password, name='changepassword'),
    path('sendverificationemail', views.send_verification_email, name='sendverificationemail'),
    path('verifyemail/<uidb64>/<token>', views.verify_email, name='verifyemail'),
]

# Configure Admin Site
admin.site.site_header = 'That Computer Scientist Administation'
admin.site.site_title = 'That Computer Scientist'
admin.site.index_title = 'Administration Area'
