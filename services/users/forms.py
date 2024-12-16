# Registration form

import string
from random import choice

from django import forms
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.blog.context_processors import avatar_list
from services.users.models import UserProfile

from .accountFunctions import store_token
from .mail_send import send_email


class RegisterForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=30,
        min_length=4,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "autocomplete": "off"}
        ),
    )
    email = forms.EmailField(
        label="Email",
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Email", "autocomplete": "off"}),
    )
    password1 = forms.CharField(
        label="Password",
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
    )
    password2 = forms.CharField(
        label="Password (again)",
        widget=forms.PasswordInput(attrs={"placeholder": "Password (again)"}),
        min_length=8,
        required=True,
    )
    captcha = forms.CharField(
        label="Captcha",
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Captcha", "autocomplete": "off"}),
    )
    expected_captcha = None
    protected_usernames = [
        "admin",
        "administrator",
        "root",
        "thatcomputerscientist",
        "skippy",
        "system",
        "test",
        "user",
        "webmaster",
        "www",
        "postmaster",
        "hostmaster",
        "info",
        "support",
        "anonymous",
        "guest",
        "nobody",
        "someone",
        "moderator",
        "moderators",
        "mods",
        "crvs",
    ]
    allowed_chars = string.ascii_letters + string.digits

    def __init__(self, *args, **kwargs):
        if "expected_captcha" in kwargs:
            self.expected_captcha = kwargs.pop("expected_captcha")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        captcha = cleaned_data.get("captcha")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if str.lower(captcha) != str.lower(self.expected_captcha):
            raise forms.ValidationError("Captcha does not match.")
        if User.objects.filter(username=cleaned_data.get("username")).exists():
            raise forms.ValidationError(
                "Username not available. Please choose another."
            )
        if cleaned_data.get("username").lower() in self.protected_usernames:
            raise forms.ValidationError(
                "Username not available. Please choose another."
            )
        for char in cleaned_data.get("username"):
            if char not in self.allowed_chars:
                raise forms.ValidationError(
                    "Username contains invalid characters. Only A-Z, a-z, and 0-9 are allowed."
                )
        if User.objects.filter(email=cleaned_data.get("email")).exists():
            raise forms.ValidationError(
                "Email already exists. Please login if this account is yours."
            )
        return cleaned_data

    def save(self, request):
        user = User.objects.create_user(
            username=self.cleaned_data.get("username").lower(),
            email=self.cleaned_data.get("email").lower(),
            password=self.cleaned_data.get("password1"),
        )
        user.save()
        user_profile = UserProfile.objects.create(user=user)
        avatar_dir = choice(list(avatar_list().keys()))
        avatar_file = choice(avatar_list()[avatar_dir])
        user_profile.avatar_url = avatar_dir + "/" + avatar_file.replace(".gif", "")
        user_profile.save()

        uid, token = store_token(token_type="verifyemail", user=user, email=user.email)

        # Send verification email
        subject = "Verify your email address"
        message = render_to_string(
            "verification_email.html",
            {
                "user": user.username if user.first_name is None else user.first_name,
                "site_name": "Shifoo",
                "uid": uid,
                "token": token,
                "protocol": "https://" if request.is_secure() else "http://",
                "domain": request.get_host(),
            },
        )
        # message = strip_tags(message)
        # send_mail(subject, message, 'Shifoo <' + settings.EMAIL_HOST_USER + '>', [user.email], fail_silently=False)
        if send_email(
            sender="noreply@thatcomputerscientist.com",
            sender_name="Shifoo",
            recipient=user.email,
            subject=subject,
            body_html=message,
            body_text=message,
        ):
            return user
        else:
            return user


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, request):
        email = self.cleaned_data.get("email")
        user = User.objects.get(email=email)
        uid, token = store_token(
            token_type="resetpassword", user=user, email=user.email
        )
        subject = "Reset your password"
        message = render_to_string(
            "reset_password_email.html",
            {
                "user": user.username if user.first_name is None else user.first_name,
                "site_name": "Shifoo",
                "uid": uid,
                "token": token,
                "protocol": "https://" if request.is_secure() else "http://",
                "domain": request.get_host(),
            },
        )
        # message = strip_tags(message)
        if send_email(
            sender="noreply@thatcomputerscientist.com",
            sender_name="Shifoo",
            recipient=user.email,
            subject=subject,
            body_html=message,
            body_text=message,
        ):
            return user
        else:
            raise forms.ValidationError("Failed to send email.")


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="New Password", widget=forms.PasswordInput, min_length=8
    )
    password2 = forms.CharField(
        label="New Password (again)", widget=forms.PasswordInput, min_length=8
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return cleaned_data

    def save(self, user):
        user.set_password(self.cleaned_data.get("password1"))
        user.save()
        return user


class UpdateUserDetailsForm(forms.Form):
    first_name = forms.CharField(
        label="First name",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "First name"}),
    )
    last_name = forms.CharField(
        label="Last name",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Last name"}),
    )
    location = forms.CharField(
        label="Location",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Location"}),
    )
    bio = forms.CharField(
        label="Bio",
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Bio"}),
    )
    is_public = forms.ChoiceField(
        label="Activity Visibility",
        choices=((True, "Public"), (False, "Private")),
        widget=forms.RadioSelect,
    )
    email_public = forms.ChoiceField(
        label="Email Visibility",
        choices=((True, "Public"), (False, "Private")),
        widget=forms.RadioSelect,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self):
        self.user.first_name = self.cleaned_data.get("first_name")
        self.user.last_name = self.cleaned_data.get("last_name")
        self.user.save()

        user_profile = UserProfile.objects.get(user=self.user)
        user_profile.location = self.cleaned_data.get("location")
        user_profile.bio = self.cleaned_data.get("bio")
        user_profile.is_public = self.cleaned_data.get("is_public")
        user_profile.email_public = self.cleaned_data.get("email_public")
        user_profile.save()

        return (self.user, user_profile)
