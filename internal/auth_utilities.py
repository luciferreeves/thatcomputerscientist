from services.users.models import UserProfile

PROTECTED_USERNAMES = [
    "admin",
    "administrator",
    "root",
    "thatcomputerscientist",
    "skippy",
    "system",
    "superuser",
    "sysadmin",
    "sysadministrator",
    "sysop",
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


def validate_auth_input(username, password, login=True):
    valid = True
    if not username or not password:
        valid = False

    if username == "" or password == "":
        valid = False

    if username in PROTECTED_USERNAMES and not login:
        valid = False

    return valid


def validate_verified_user_email(user):
    try:
        email_verified = UserProfile.objects.get(user=user).email_verified
    except UserProfile.DoesNotExist:
        email_verified = False
    return email_verified
