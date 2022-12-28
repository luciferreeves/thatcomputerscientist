# Registration form

from django import forms
from django.contrib.auth.models import User
from users.models import UserProfile
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token

class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30, min_length=4)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password (again)', widget=forms.PasswordInput)
    captcha = forms.CharField(label='Captcha', max_length=6)
    expected_captcha = None

    def __init__(self, *args, **kwargs):
        if 'expected_captcha' in kwargs:
            self.expected_captcha = kwargs.pop('expected_captcha')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        captcha = cleaned_data.get('captcha')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Passwords do not match.')
        if str.lower(captcha) != str.lower(self.expected_captcha):
            raise forms.ValidationError('Captcha does not match.')
        if User.objects.filter(username=cleaned_data.get('username')).exists():
            raise forms.ValidationError('Username already exists.')
        if User.objects.filter(email=cleaned_data.get('email')).exists():
            raise forms.ValidationError('Email already exists.')
        return cleaned_data

    def save(self, request):
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('password1'),
        )
        user.save()
        user_profile = UserProfile.objects.create(user=user)
        user_profile.save()

        # Send verification email
        subject = 'Verify your email address'
        message = render_to_string('verification_email.html', {
            'user': user.username if user.first_name is None else user.first_name,
            'site_name': 'That Computer Scientist',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'protocol': 'https://' if request.is_secure() else 'http://',
            'domain': request.get_host(),
        })
        message = strip_tags(message)
        send_mail(subject, message, 'That Computer Scientist <' + settings.EMAIL_HOST_USER + '>', [user.email], fail_silently=False)

        return user

