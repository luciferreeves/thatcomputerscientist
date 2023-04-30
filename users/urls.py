from django.urls import path
from . import views
from django.contrib import admin

app_name = 'users'
urlpatterns = [
    path('/login', views.login_user, name='login'),
    path('/logout', views.logout_user, name='logout'),
    path('/update', views.update_user, name='update'),
    path('/changepassword', views.change_password, name='changepassword'),
    path('/sendchangeuseremail', views.send_change_user_email, name='sendchangeuseremail'),
    path('/sendverificationemail', views.send_verification_email, name='sendverificationemail'),
    path('/updateavatar', views.update_avatar, name='updateavatar'),
    path('/updateblinkies', views.update_blinkie, name='updateblinkie'),
    path('/delete', views.delete_user, name='delete'),
    path('/<mode>/<uid>/<token>', views.verify_email, name='verifyemail'),
    path('/<mode>/<uid>/<token>', views.verify_email, name='changeemail'),
]

# Configure Admin Site
admin.site.site_header = 'That Computer Scientist Administation'
admin.site.site_title = 'That Computer Scientist'
admin.site.index_title = 'Administration Area'
