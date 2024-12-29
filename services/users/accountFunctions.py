import secrets
import uuid

from django.utils import timezone

from services.users.models import TokenStore, UserProfile


def generate_token():
    uid = uuid.uuid4().hex
    token = secrets.token_urlsafe(32)
    print(uid, token)
    return uid, token


def store_token(token_type, user, email=None):
    previous_tokens = TokenStore.objects.filter(user=user, token_type=token_type)
    if previous_tokens.exists():
        previous_tokens.delete()
    uid, token = generate_token()
    token_store = TokenStore.objects.create(
        user=user,
        email=email if email is not None else user.email,
        uid=uid,
        token=token,
        token_type=token_type,
        expires=timezone.now() + timezone.timedelta(minutes=30),
    )
    token_store.save()
    return uid, token


def verify_token(token_type, uid, token, hold_verification=False):
    try:
        token_store = TokenStore.objects.get(
            token_type=token_type, uid=uid, token=token
        )
        if (
            token_store.expires > timezone.now()
            and not token_store.verified
            and token_store.token_type == token_type
            and token_store.uid == uid
            and token_store.token == token
        ):

            if hold_verification:
                return token_store
            token_store.verified = True

            if token_type == "verifyemail":
                UserProfile.objects.filter(user=token_store.user).update(
                    email_verified=True
                )

            token_store.save()

        return token_store
    except TokenStore.DoesNotExist:
        return None
