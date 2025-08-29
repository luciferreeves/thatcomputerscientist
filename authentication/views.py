from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect
from users.functions import email_verified

def login(request):
    next = request.POST.get("next", "core:home").strip()
    username = request.POST.get("username")
    password = request.POST.get("password")

    print("Next:", next)
    print("Username:", username)
    print("Password:", password)
    if username == "" or password == "" or username is None or password is None:
        messages.error(request, "ErrorEmptyFields", extra_tags="LoginError")
        return redirect(f"{next}?username={username}" if username else next)
    else:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if email_verified(user):
                auth_login(request, user)
                return redirect(next)
            else:
                messages.error(request, "ErrorEmailNotVerified", extra_tags="LoginError")
                return redirect(f"{next}?username={username}")
        else:
            messages.error(request, "ErrorInvalidCredentials", extra_tags="LoginError")
            return redirect(f"{next}?username={username}")


def logout(request):
    auth_logout(request)
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)
