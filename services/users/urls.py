from django.contrib import admin
from django.urls import path

from . import views

app_name = "auth"
urlpatterns = [
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    # path("/update", views.update_user, name="update"),
    # path("/changepassword", views.change_password, name="changepassword"),
    # path(
    #     "/sendchangeuseremail", views.send_change_user_email, name="sendchangeuseremail"
    # ),
    # path(
    #     "/sendverificationemail",
    #     views.send_verification_email,
    #     name="sendverificationemail",
    # ),
    # path("/updateavatar", views.update_avatar, name="updateavatar"),
    # path("/updateblinkies", views.update_blinkie, name="updateblinkie"),
    # path("/delete", views.delete_user, name="delete"),
    # path("/<mode>/<uid>/<token>", views.verify_email, name="verifyemail"),
    # path("/<mode>/<uid>/<token>", views.verify_email, name="changeemail"),
    # path("/resetpassword/<uid>/<token>", views.reset_password, name="resetpassword"),
]

# Configure Admin Site
