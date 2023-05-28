import uuid
from django.core.cache import cache

class UserUUIDMiddleware:
    # assign a uuid to the user if they don't have one
    # store in cookies for 365 days
    def __init__(self, get_response):
        self.get_response = get_response
        self.cookie_name = 'user_uuid'

    def __call__(self, request):
        if not request.COOKIES.get(self.cookie_name):
            response = self.get_response(request)
            response.set_cookie(self.cookie_name, uuid.uuid4(), max_age=31536000)
            return response
        return self.get_response(request)

def userTrackingContextProcessor(request):
    # user tracking context processor - track 3 types of users (anonymous, logged in, admin)
    # based on the user's uuid cookie. Only UUID are necessary to track online users. Then we
    # separate them into anonymous, logged in, and admin users based on their permissions.

    # get the user's uuid from the cookie
    user_uuid = request.COOKIES.get('user_uuid')

    # get the user's permissions
    is_authenticated = request.user.is_authenticated
    is_staff = request.user.is_staff

    # get a list of anonymous users (retire after 60 seconds)
    anonymous_users = cache.get('anonymous_users', set())
    logged_in_users = cache.get('logged_in_users', set())
    admin_users = cache.get('admin_users', set())

    if not is_authenticated:
        anonymous_users.add(user_uuid)
        logged_in_users.discard(user_uuid)
        admin_users.discard(user_uuid)
    elif is_staff and is_authenticated:
        admin_users.add(user_uuid)
        anonymous_users.discard(user_uuid)
        logged_in_users.discard(user_uuid)
    else:
        logged_in_users.add(user_uuid)
        anonymous_users.discard(user_uuid)
        admin_users.discard(user_uuid)
    cache.set('anonymous_users', anonymous_users, 300)
    cache.set('logged_in_users', logged_in_users, 300)
    cache.set('admin_users', admin_users, 300)

    anonymous_users = cache.get('anonymous_users', set())
    logged_in_users = cache.get('logged_in_users', set())
    admin_users = cache.get('admin_users', set())

    return {
        'anonymous_users': len(anonymous_users),
        'logged_in_users': len(logged_in_users),
        'admin_users': len(admin_users),
    }

